# Roadmap

## Autenticación: OK

- `/auth/register` → `/auth/login` → `/auth/refresh-token`

## Verificación: OK

- `/verification/verify-email/{uuid}`

## Gestión del Perfil Inicial: OK (faltan tests de edit y change)

- `/user/profile` → `/user/edit-profile` → `/user/change-email`

## Seguridad Avanzada: TODO

- `/verification/enable-2fa` → `/verification/verify-2fa`

## Recuperación y Seguridad: TODO

- `/auth/forgot-password` → `/auth/reset-password` → `/auth/logout`

## Gestión del Usuario Avanzada: TODO

- `/user/change-password` → `/user/delete-account`
