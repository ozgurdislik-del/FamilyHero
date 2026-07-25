# ADR-002: İzin Tabanlı Yetkilendirme

## Karar
Sabit rol kontrolleri yerine RBAC kullanılacaktır: `roles`, `permissions`, `role_permissions`, `membership_roles`.

## Hedef kullanım
`current_user.can("task.create")` ve `@permission_required("task.create")`.

## Sonuç
Yeni roller ve modüller kodun her yerinde koşul değiştirmeden eklenebilir.
