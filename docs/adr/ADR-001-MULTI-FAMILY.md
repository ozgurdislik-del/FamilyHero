# ADR-001: Kullanıcı–Aile Üyelik Modeli

## Karar
Kullanıcıya doğrudan `family_id` eklemek yerine `family_memberships` ara tablosu kullanılacaktır.

## Gerekçe
Bir kullanıcı gelecekte birden fazla aileye, velayet grubuna veya kurum alanına katılabilir. Üyelik tablosu rolü, durumu ve aile bağlamını üyelik seviyesinde tutar.

## Geçiş
Mevcut `children` ve `admins` tabloları hemen kaldırılmayacak; yeni kimlik modeline aşamalı olarak bağlanacaktır.
