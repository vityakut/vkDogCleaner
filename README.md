# vkDogCleaner
Delete blocked users from your vk publics

### config.toml
```toml
#login - имя пользователя
login = ""
# password - пароль
password = ""


# groups - список групп для очистки
groups = [
  "",
  ]


# clear_mode - режим очистки собак
  #  0 - удалить всех собак
  #  1 - в процентах
  #  2 - в штуках
  #  3 - в процентах (clear_percent) но не более установленного значения (clear_count)
#
clear_mode = 2
# clear_percent - количество собак для очистки в процентах при clear_mode = 1
clear_percent = 10
# clear_count - количество собак для очистки в штуках при clear_mode = 2
clear_count = 20



[app]
#id приложения для авторизации
id = "4586650"
#antigate  - token для доступа к антикапче
antigate = ""
```

