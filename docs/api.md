---
hide:
  - navigation
---

# Definição de rotas

Nesta seção, serão definidas as rotas da API, bem como os métodos HTTP e os parâmetros necessários para cada uma delas.

## Autenticação do Google

**Método HTTP:** `POST` <br>
**Rota:** `/users/register`

Esta rota permite ao usuário fazer o login usando o Google OAuth2. Caso o usuário não tenha uma conta, uma nova será criada.

**Request:**

O request deve conter um token de autenticação do Google.

```js linenums="1"
body = {
  access_token: "token",
};
```

- `"access_token"`: O token de acesso do Google OAuth2.

**Response:**

A resposta conterá informações de autenticação bem-sucedida, incluindo um token de autenticação.

**Success (200 OK)**

```js linenums="1"
(headers = {
  "Content-Type": "application/json",
  "Set-Cookie":
    "refresh=<refresh-token>; Secure; HttpOnly; SameSite=Lax; Expires=<expires-date>",
}),
  (body = {
    access: "token",
    first_name: "name",
    last_name: "name",
    email: "email",
    picture_url: "picture_url",
  });
```

**Error (400 BAD REQUEST)**

```js linenums="1"
body = {
  errors: "descriptive error message",
};
```

## Login

**Método HTTP:** `POST` <br>
**Rota:** `/users/login`

Esta rota atualiza o _refresh-token_ do usuário e retorna um novo _access-token_.

**Request:**

O request deve conter um _refresh-token_.

```js linenums="1"
headers = {
  Cookie: "refresh=<refresh-token>",
};
```

**Response:**

**Success (200 OK)**

```js linenums="1"
(headers = {
  "Set-Cookie":
    "refresh=<refresh-token>; Secure; HttpOnly; SameSite=Lax; Expires=<expires-date>",
}),
  (body = {
    access: "token",
    first_name: "name",
    last_name: "name",
    email: "email",
    picture_url: "picture_url",
  });
```

## Logout

**Método HTTP:** `POST` <br>
**Rota:** `users/logout`

Esta rota permite ao usuário fazer logout de sua conta no site.

**Request:**

```js linenums="1"
headers = {
  Cookie: "refresh=<refresh-token>",
};
```

**Response:**

**Suceess (200 OK)**

**Error (400 BAD REQUEST)**

**Error (401 UNAUTHORIZED)**

**OBSERVAÇÃO:** As respostas não contém conteúdo.
