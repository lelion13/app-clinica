# Cambios activos

Cada **subcarpeta** representa un trabajo en curso o recién terminado antes de archivar.

## Crear un cambio nuevo

1. Elegí nombre `kebab-case`.
2. Creá `openspec/changes/<nombre>/`.
3. Copiá [`../templates/cambio.md`](../templates/cambio.md) y completá secciones (o dividí en `proposal.md`, `spec.md`, …).
4. Implementá en el código siguiendo `tasks.md` o la lista acordada.

## Archivar

Cuando el cambio esté fusionado y verificado, mové la carpeta a `archive/`:

- `openspec/changes/mi-feature/` → `openspec/changes/archive/mi-feature/`

Opcional: añadí un `README.md` dentro del archivo con fecha de cierre y enlace al PR.
