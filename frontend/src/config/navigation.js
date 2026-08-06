/** Rutas y etiquetas del menú; alineado con RBAC backend. */

export const DISTRIBUTION_ITEMS = [
  { label: "Ocupación semanal", path: "/ocupacion-semanal", roles: ["admin", "operador"] },
  { label: "Ocupación", path: "/ocupacion", roles: ["admin", "operador"] },
  { label: "Agenda ocupación", path: "/agenda-ocupacion", roles: ["admin", "operador"] },
  { label: "Indicadores ocupación", path: "/indicadores-ocupacion", roles: ["admin", "operador"] },
  { label: "Agenda", path: "/agenda", roles: ["admin", "operador"] },
  { label: "Ubicaciones", path: "/ubicaciones", roles: ["admin", "operador"] },
  { label: "Profesionales", path: "/profesionales", roles: ["admin", "operador"] },
  { label: "Consultorios", path: "/consultorios", roles: ["admin", "operador"] },
  { label: "Horarios consultorio", path: "/horarios-consultorio", roles: ["admin", "operador"] },
  { label: "Estadística", path: "/estadisticas", roles: ["admin", "operador"] },
];

export const NOVEDADES_ITEMS = [
  { label: "Carga módulos", path: "/novedades/carga", roles: ["admin", "jefe_medico"] },
  { label: "Mis profesionales", path: "/novedades/mis-profesionales", roles: ["admin", "rrhh", "jefe_medico"] },
  { label: "Capital Humano", path: "/novedades/xls", roles: ["admin", "rrhh"] },
  { label: "Parametrización", path: "/novedades/parametrizacion", roles: ["admin", "rrhh"] },
];

export const USERS_NAV_ITEM = {
  label: "Usuarios",
  path: "/usuarios",
  roles: ["admin"],
};

export const DISTRIBUTION_PATHS = DISTRIBUTION_ITEMS.map((item) => item.path);
export const NOVEDADES_PATHS = NOVEDADES_ITEMS.map((item) => item.path);

export function isDistributionPath(pathname) {
  return DISTRIBUTION_PATHS.includes(pathname);
}

export function isNovedadesPath(pathname) {
  return NOVEDADES_PATHS.includes(pathname) || pathname.startsWith("/novedades/");
}

export function canAccessModule(userRole, allowedRoles) {
  return Boolean(userRole && allowedRoles.includes(userRole));
}

export function itemsForRole(items, userRole) {
  return items.filter((item) => canAccessModule(userRole, item.roles));
}
