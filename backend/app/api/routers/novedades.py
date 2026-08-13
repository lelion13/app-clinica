from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin_or_jefe, require_admin_or_rrhh, require_novedades_reader
from app.db.session import get_db
from app.models.novedades import NOVEDAD_TIPO_LABELS, NovedadTipo, PeriodoEstado
from app.models.user import User, UserRole
from app.schemas.novedades import (
    AsignacionCreateRequest,
    AsignacionResponse,
    AsignacionUpdateRequest,
    AjusteCapitalCreateRequest,
    AjusteCapitalResponse,
    BonosImportRequest,
    BonosImportResponse,
    CapitalHumanoGridResponse,
    GridRowResponse,
    SoloBonoRowResponse,
    JefeServicioCreateRequest,
    JefeServicioResponse,
    ModuloCreateRequest,
    ModuloResponse,
    ModuloServiciosUpdateRequest,
    ModuloUpdateRequest,
    NovedadCreateRequest,
    NovedadResponse,
    NovedadUpdateRequest,
    NovedadesProfSyncResponse,
    NovedadesTransaccionalPurgeResponse,
    PeriodoCreateRequest,
    PeriodoResponse,
    ProfesionalDirectoryItem,
    ProfesionalServicioCreateRequest,
    ProfesionalServicioResponse,
    ServicioCreateRequest,
    ServicioResponse,
    ServicioUpdateRequest,
    TieneProduccionResponse,
)
from app.services.novedades import cargas as cargas_service
from app.services.novedades import bonos_import as bonos_import_service
from app.services.novedades import capital_humano as capital_humano_service
from app.services.novedades import export_xls
from app.services.novedades import masters as masters_service
from app.services.novedades import prof_sync as prof_sync_service
from app.services.novedades import purge as purge_service
from app.services.novedades import tiene_produccion as tiene_produccion_service
from app.services.novedades.helpers import get_servicio_or_404, list_servicios_for_user
from app.services.novedades.professional_directory import list_professionals_for_servicio

router = APIRouter()


class JefeCandidatoResponse(BaseModel):
    id: int
    name: str
    email: str


def _servicio_response(item) -> ServicioResponse:
    return ServicioResponse(
        id=item.id,
        nombre=item.nombre,
        activo=item.activo,
        valor_hora=item.valor_hora,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _modulo_response(db: Session, item) -> ModuloResponse:
    return ModuloResponse(
        id=item.id,
        descripcion=item.descripcion,
        comentario=item.comentario,
        valor=item.valor,
        produccion=bool(getattr(item, "produccion", False)),
        servicio_ids=masters_service.list_modulo_servicio_ids(db, item.id),
        servicio_nombres=masters_service.list_modulo_servicio_nombres(db, item.id),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _periodo_response(item) -> PeriodoResponse:
    estado = item.estado.value if isinstance(item.estado, PeriodoEstado) else str(item.estado)
    return PeriodoResponse(
        id=item.id,
        nombre=item.nombre,
        fecha_inicio=item.fecha_inicio,
        fecha_fin=item.fecha_fin,
        estado=estado,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _novedad_response(db: Session, item) -> NovedadResponse:
    from app.models.novedades import NovedadesPeriodo, NovedadesProfesional

    tipo = item.tipo if isinstance(item.tipo, NovedadTipo) else NovedadTipo(item.tipo)
    servicio = get_servicio_or_404(db, item.servicio_id)
    valor_hora = servicio.valor_hora
    professional = db.execute(
        select(NovedadesProfesional).where(NovedadesProfesional.id == item.professional_id)
    ).scalar_one_or_none()
    periodo = db.execute(
        select(NovedadesPeriodo).where(NovedadesPeriodo.id == item.periodo_id)
    ).scalar_one_or_none()
    return NovedadResponse(
        id=item.id,
        periodo_id=item.periodo_id,
        periodo_nombre=periodo.nombre if periodo else None,
        servicio_id=item.servicio_id,
        servicio_nombre=servicio.nombre,
        professional_id=item.professional_id,
        professional_name=professional.full_name if professional else None,
        professional_codprof=professional.codprof if professional else None,
        tipo=tipo.value,
        tipo_label=NOVEDAD_TIPO_LABELS.get(tipo, tipo.value),
        horas=item.horas,
        valor_calculado=item.horas * valor_hora,
        fecha_realizacion=item.fecha_realizacion,
        motivo_sin_produccion=item.motivo_sin_produccion,
        observacion_sin_produccion=item.observacion_sin_produccion,
        created_at=item.created_at,
        updated_at=item.updated_at,
        created_by=item.created_by,
    )


def _asignacion_response(db: Session, item) -> AsignacionResponse:
    from app.models.novedades import NovedadesModulo, NovedadesPeriodo, NovedadesProfesional

    modulo = db.execute(select(NovedadesModulo).where(NovedadesModulo.id == item.modulo_id)).scalar_one_or_none()
    servicio = get_servicio_or_404(db, item.servicio_id)
    professional = db.execute(
        select(NovedadesProfesional).where(NovedadesProfesional.id == item.professional_id)
    ).scalar_one_or_none()
    periodo = db.execute(
        select(NovedadesPeriodo).where(NovedadesPeriodo.id == item.periodo_id)
    ).scalar_one_or_none()
    return AsignacionResponse(
        id=item.id,
        periodo_id=item.periodo_id,
        periodo_nombre=periodo.nombre if periodo else None,
        servicio_id=item.servicio_id,
        servicio_nombre=servicio.nombre,
        professional_id=item.professional_id,
        professional_name=professional.full_name if professional else None,
        professional_codprof=professional.codprof if professional else None,
        modulo_id=item.modulo_id,
        modulo_descripcion=modulo.descripcion if modulo else None,
        modulo_valor=modulo.valor if modulo else None,
        fecha_realizacion=item.fecha_realizacion,
        motivo_sin_produccion=item.motivo_sin_produccion,
        observacion_sin_produccion=item.observacion_sin_produccion,
        created_at=item.created_at,
        updated_at=item.updated_at,
        created_by=item.created_by,
    )


@router.get("/bonos/tiene-produccion", response_model=TieneProduccionResponse)
def bonos_tiene_produccion(
    fecha: str = Query(...),
    codprof: str = Query(...),
    user: User = Depends(require_admin_or_jefe),
) -> TieneProduccionResponse:
    _ = user
    return tiene_produccion_service.check_tiene_produccion(fecha=fecha, codprof=codprof)


@router.get("/jefes-candidatos", response_model=list[JefeCandidatoResponse])
def jefes_candidatos(db: Session = Depends(get_db), user: User = Depends(require_admin_or_rrhh)) -> list[JefeCandidatoResponse]:
    _ = user
    rows = list(
        db.execute(
            select(User).where(User.deleted_at.is_(None), User.role == UserRole.jefe_medico, User.is_active.is_(True)).order_by(User.name)
        )
        .scalars()
        .all()
    )
    return [JefeCandidatoResponse(id=row.id, name=row.name, email=row.email) for row in rows]


@router.get("/servicios", response_model=list[ServicioResponse])
def servicios_list(db: Session = Depends(get_db), user: User = Depends(require_novedades_reader)) -> list[ServicioResponse]:
    items = list_servicios_for_user(db, user) if user.role == UserRole.jefe_medico else masters_service.list_servicios(db)
    return [_servicio_response(item) for item in items]


@router.post("/servicios", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def servicios_create(
    payload: ServicioCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> ServicioResponse:
    return _servicio_response(masters_service.create_servicio(db, payload, actor_id=user.id))


@router.put("/servicios/{servicio_id}", response_model=ServicioResponse)
def servicios_update(
    servicio_id: int,
    payload: ServicioUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> ServicioResponse:
    return _servicio_response(masters_service.update_servicio(db, servicio_id, payload, actor_id=user.id))


@router.delete("/servicios/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def servicios_delete(
    servicio_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> None:
    masters_service.delete_servicio(db, servicio_id, actor_id=user.id)


@router.get("/modulos", response_model=list[ModuloResponse])
def modulos_list(
    servicio_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_novedades_reader),
) -> list[ModuloResponse]:
    _ = user
    return [_modulo_response(db, item) for item in masters_service.list_modulos(db, servicio_id=servicio_id)]


@router.post("/modulos", response_model=ModuloResponse, status_code=status.HTTP_201_CREATED)
def modulos_create(
    payload: ModuloCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> ModuloResponse:
    item = masters_service.create_modulo(db, payload, actor_id=user.id)
    return _modulo_response(db, item)


@router.put("/modulos/{modulo_id}", response_model=ModuloResponse)
def modulos_update(
    modulo_id: int,
    payload: ModuloUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> ModuloResponse:
    item = masters_service.update_modulo(db, modulo_id, payload, actor_id=user.id)
    return _modulo_response(db, item)


@router.put("/modulos/{modulo_id}/servicios", response_model=ModuloResponse)
def modulos_update_servicios(
    modulo_id: int,
    payload: ModuloServiciosUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> ModuloResponse:
    item = masters_service.update_modulo_servicios(
        db, modulo_id, payload.servicio_ids, actor_id=user.id
    )
    return _modulo_response(db, item)


@router.delete("/modulos/{modulo_id}", status_code=status.HTTP_204_NO_CONTENT)
def modulos_delete(
    modulo_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> None:
    masters_service.delete_modulo(db, modulo_id, actor_id=user.id)


@router.get("/periodos", response_model=list[PeriodoResponse])
def periodos_list(db: Session = Depends(get_db), user: User = Depends(require_novedades_reader)) -> list[PeriodoResponse]:
    _ = user
    return [_periodo_response(item) for item in cargas_service.list_periodos(db)]


@router.post("/periodos", response_model=PeriodoResponse, status_code=status.HTTP_201_CREATED)
def periodos_create(
    payload: PeriodoCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> PeriodoResponse:
    return _periodo_response(cargas_service.create_periodo(db, payload, actor_id=user.id))


@router.post("/periodos/{periodo_id}/cerrar", response_model=PeriodoResponse)
def periodos_cerrar(
    periodo_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> PeriodoResponse:
    return _periodo_response(cargas_service.close_periodo(db, periodo_id, actor_id=user.id))


@router.post("/periodos/{periodo_id}/reabrir", response_model=PeriodoResponse)
def periodos_reabrir(
    periodo_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> PeriodoResponse:
    return _periodo_response(cargas_service.reopen_periodo(db, periodo_id, actor_id=user.id))


@router.get("/jefe-servicios", response_model=list[JefeServicioResponse])
def jefe_servicios_list(db: Session = Depends(get_db), user: User = Depends(require_admin_or_rrhh)) -> list[JefeServicioResponse]:
    _ = user
    result = []
    for link, linked_user, servicio in cargas_service.list_jefe_servicios(db):
        result.append(
            JefeServicioResponse(
                id=link.id,
                user_id=link.user_id,
                user_name=linked_user.name if linked_user else None,
                user_email=linked_user.email if linked_user else None,
                servicio_id=link.servicio_id,
                servicio_nombre=servicio.nombre if servicio else None,
                created_at=link.created_at,
            )
        )
    return result


@router.post("/jefe-servicios", response_model=JefeServicioResponse, status_code=status.HTTP_201_CREATED)
def jefe_servicios_create(
    payload: JefeServicioCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> JefeServicioResponse:
    item = cargas_service.create_jefe_servicio(db, payload, actor_id=user.id)
    rows = cargas_service.list_jefe_servicios(db)
    for link, linked_user, servicio in rows:
        if link.id == item.id:
            return JefeServicioResponse(
                id=link.id,
                user_id=link.user_id,
                user_name=linked_user.name if linked_user else None,
                user_email=linked_user.email if linked_user else None,
                servicio_id=link.servicio_id,
                servicio_nombre=servicio.nombre if servicio else None,
                created_at=link.created_at,
            )
    return JefeServicioResponse(
        id=item.id,
        user_id=item.user_id,
        servicio_id=item.servicio_id,
        created_at=item.created_at,
    )


@router.delete("/jefe-servicios/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def jefe_servicios_delete(
    link_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> None:
    cargas_service.delete_jefe_servicio(db, link_id, actor_id=user.id)


@router.get("/profesional-servicios", response_model=list[ProfesionalServicioResponse])
def profesional_servicios_list(
    db: Session = Depends(get_db), user: User = Depends(require_novedades_reader)
) -> list[ProfesionalServicioResponse]:
    result = []
    for link, professional, servicio in cargas_service.list_profesional_servicios(db, user):
        result.append(
            ProfesionalServicioResponse(
                id=link.id,
                professional_id=link.professional_id,
                professional_name=professional.full_name if professional else None,
                professional_codprof=professional.codprof if professional else None,
                professional_is_active=professional.is_active if professional else None,
                servicio_id=link.servicio_id,
                servicio_nombre=servicio.nombre if servicio else None,
                created_at=link.created_at,
            )
        )
    return result


@router.post("/profesional-servicios", response_model=ProfesionalServicioResponse, status_code=status.HTTP_201_CREATED)
def profesional_servicios_create(
    payload: ProfesionalServicioCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_novedades_reader),
) -> ProfesionalServicioResponse:
    item = cargas_service.create_profesional_servicio(db, payload, user=user)
    return ProfesionalServicioResponse(
        id=item.id,
        professional_id=item.professional_id,
        servicio_id=item.servicio_id,
        created_at=item.created_at,
    )


@router.delete("/profesional-servicios/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def profesional_servicios_delete(
    link_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_novedades_reader),
) -> None:
    cargas_service.delete_profesional_servicio(db, link_id, user=user)


@router.get("/profesionales", response_model=list[ProfesionalDirectoryItem])
def profesionales_directory(
    servicio_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    exclude_linked: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(require_novedades_reader),
) -> list[ProfesionalDirectoryItem]:
    _ = user
    return list_professionals_for_servicio(
        db, servicio_id=servicio_id, q=q, exclude_linked=exclude_linked
    )


@router.post("/profesionales/sync", response_model=NovedadesProfSyncResponse)
def profesionales_sync(
    db: Session = Depends(get_db),
    user: User = Depends(require_novedades_reader),
) -> NovedadesProfSyncResponse:
    return prof_sync_service.sync_novedades_professionals(db, actor_id=user.id)


@router.post("/transaccional/purge", response_model=NovedadesTransaccionalPurgeResponse)
def transaccional_purge(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> NovedadesTransaccionalPurgeResponse:
    return purge_service.purge_novedades_transaccional(db, user=user)


@router.get("/asignaciones-modulos", response_model=list[AsignacionResponse])
def asignaciones_list(db: Session = Depends(get_db), user: User = Depends(require_admin_or_jefe)) -> list[AsignacionResponse]:
    return [_asignacion_response(db, item) for item in cargas_service.list_asignaciones(db, user)]


@router.post("/asignaciones-modulos", response_model=AsignacionResponse, status_code=status.HTTP_201_CREATED)
def asignaciones_create(
    payload: AsignacionCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_jefe),
) -> AsignacionResponse:
    item = cargas_service.create_asignacion(db, payload, user=user)
    return _asignacion_response(db, item)


@router.put("/asignaciones-modulos/{item_id}", response_model=AsignacionResponse)
def asignaciones_update(
    item_id: int,
    payload: AsignacionUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_jefe),
) -> AsignacionResponse:
    item = cargas_service.update_asignacion(db, item_id, payload, user=user)
    return _asignacion_response(db, item)


@router.delete("/asignaciones-modulos/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def asignaciones_delete(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_jefe),
) -> None:
    cargas_service.delete_asignacion(db, item_id, user=user)


@router.get("/cargas", response_model=list[NovedadResponse])
def novedades_list(db: Session = Depends(get_db), user: User = Depends(require_admin_or_jefe)) -> list[NovedadResponse]:
    return [_novedad_response(db, item) for item in cargas_service.list_novedades(db, user)]


@router.post("/cargas", response_model=NovedadResponse, status_code=status.HTTP_201_CREATED)
def novedades_create(
    payload: NovedadCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_jefe),
) -> NovedadResponse:
    item = cargas_service.create_novedad(db, payload, user=user)
    return _novedad_response(db, item)


@router.put("/cargas/{item_id}", response_model=NovedadResponse)
def novedades_update(
    item_id: int,
    payload: NovedadUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_jefe),
) -> NovedadResponse:
    item = cargas_service.update_novedad(db, item_id, payload, user=user)
    return _novedad_response(db, item)


@router.delete("/cargas/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def novedades_delete(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_jefe),
) -> None:
    cargas_service.delete_novedad(db, item_id, user=user)


@router.get("/grilla", response_model=list[GridRowResponse])
def grilla_list(
    periodo_id: int | None = Query(default=None),
    servicio_id: int | None = Query(default=None),
    professional_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    concepto: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> list[GridRowResponse]:
    _ = user
    return export_xls.build_grid_rows(
        db,
        periodo_id=periodo_id,
        servicio_id=servicio_id,
        professional_id=professional_id,
        q=q,
        concepto_q=concepto,
    )


@router.get("/capital-humano", response_model=CapitalHumanoGridResponse)
def capital_humano_list(
    periodo_id: int | None = Query(default=None),
    servicio_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> CapitalHumanoGridResponse:
    _ = user
    return capital_humano_service.build_capital_humano_grid(
        db, periodo_id=periodo_id, servicio_id=servicio_id, q=q
    )


@router.post(
    "/capital-humano/bonos/import",
    response_model=BonosImportResponse,
    status_code=status.HTTP_200_OK,
)
def capital_humano_bonos_import(
    payload: BonosImportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> BonosImportResponse:
    return bonos_import_service.import_bonos_for_periodo(db, payload.periodo_id, user)


@router.get("/capital-humano/bonos/solo", response_model=list[SoloBonoRowResponse])
def capital_humano_bonos_solo(
    periodo_id: int = Query(...),
    servicio_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> list[SoloBonoRowResponse]:
    _ = user
    return bonos_import_service.list_solo_bonos(db, periodo_id=periodo_id, servicio_id=servicio_id)


@router.get("/capital-humano/ajustes", response_model=list[AjusteCapitalResponse])
def capital_humano_ajustes_list(
    professional_id: int = Query(...),
    periodo_id: int = Query(...),
    servicio_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> list[AjusteCapitalResponse]:
    _ = user
    return capital_humano_service.list_ajustes(
        db, professional_id=professional_id, periodo_id=periodo_id, servicio_id=servicio_id
    )


@router.post("/capital-humano/ajustes", response_model=AjusteCapitalResponse, status_code=status.HTTP_201_CREATED)
def capital_humano_ajustes_create(
    payload: AjusteCapitalCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> AjusteCapitalResponse:
    return capital_humano_service.create_ajuste(db, payload, user=user)


@router.get("/export.xlsx")
def export_xlsx(
    periodo_id: int | None = Query(default=None),
    servicio_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    concepto: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> Response:
    _ = user
    content = export_xls.export_xlsx_bytes(db, periodo_id=periodo_id, servicio_id=servicio_id, q=q, concepto_q=concepto)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="novedades-detalle.xlsx"'},
    )


@router.get("/export-capital.xlsx")
def export_capital_xlsx(
    periodo_id: int | None = Query(default=None),
    servicio_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> Response:
    _ = user
    content = capital_humano_service.export_capital_xlsx_bytes(
        db, periodo_id=periodo_id, servicio_id=servicio_id, q=q
    )
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="capital-humano.xlsx"'},
    )


@router.get("/export-capital-bonos.xlsx")
def export_capital_bonos_xlsx(
    periodo_id: int | None = Query(default=None),
    servicio_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_rrhh),
) -> Response:
    _ = user
    content = capital_humano_service.export_capital_bonos_xlsx_bytes(
        db, periodo_id=periodo_id, servicio_id=servicio_id, q=q
    )
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="capital-humano-bonos.xlsx"'},
    )
