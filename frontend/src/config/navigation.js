/** Rutas y etiquetas del menú; alineado con RBAC backend (admin / operador). */

export const DISTRIBUTION_ITEMS = [
  { label: "Ocupación semanal", path: "/ocupacion-semanal", roles: ["admin", "operador"] },
  { label: "Agenda", path: "/agenda", roles: ["admin", "operador"] },
  { label: "Ubicaciones", path: "/ubicaciones", roles: ["admin", "operador"] },
  { label: "Profesionales", path: "/profesionales", roles: ["admin", "operador"] },
  { label: "Consultorios", path: "/consultorios", roles: ["admin", "operador"] },
  { label: "Horarios consultorio", path: "/horarios-consultorio", roles: ["admin", "operador"] },
  { label: "Estadística", path: "/estadisticas", roles: ["admin", "operador"] },
];

export const USERS_NAV_ITEM = {
  label: "Usuarios",
  path: "/usuarios",
  roles: ["admin"],
};

export const DISTRIBUTION_PATHS = DISTRIBUTION_ITEMS.map((item) => item.path);

export function isDistributionPath(pathname) {
  return DISTRIBUTION_PATHS.includes(pathname);
}

export function canAccessModule(userRole, allowedRoles) {
  return Boolean(userRole && allowedRoles.includes(userRole));
}

export function itemsForRole(items, userRole) {
  return items.filter((item) => canAccessModule(userRole, item.roles));
}
