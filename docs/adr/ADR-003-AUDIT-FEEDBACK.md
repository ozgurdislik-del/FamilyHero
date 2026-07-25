# ADR-003: Audit Log ve Feedback Çekirdeği

## Karar
Kritik işlemler `audit_logs` tablosuna; hata, öneri ve şikâyetler `feedback_items` ve `feedback_comments` tablolarına yazılacaktır.

## Gizlilik
Audit kaydı gerekli olay bilgisini tutar; parola ve hassas içerik kaydedilmez.
