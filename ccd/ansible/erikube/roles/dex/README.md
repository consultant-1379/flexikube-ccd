
# Dex

dex - A federated OpenID Connect provider

https://github.com/coreos/dex

Dex deployed on Kubernetes as a deployment using custom resource definitions
as a storage backend.

# Configuration

Some example configuration below

## Issuer URL

TBD

### TLS secret

Pre-generated *dex_cert_file* and *dex_key_file* variables can be defined as variables.
If these are not defined, a self-signed certificate is generated as part of deployment.
This certificate will be automatically added as a trusted certificate in master and
director nodes (IBD only). In either case, a k8s secret named *dex-tls* will be created.


### Ingress with TLS termination

The dex role will configure an ingress with TLS termination in the ingress load balancer.

Dex will create a key and certificate, if it is not defined in the
inventory.  Configure certificate and key files as in the TLS secret example (or create
the secret manually with the name *dex-tls*)

The variable *dex_ingress_host* is used to create a **name based virtual host**
ingress resource with TLS termination using the *dex-tls* secret. Example:

```
dex_ingress_host: auth.example.com
```

### Ingress with TLS pass-through

TBD

## Backend connectors

Dex will not start without a configured connector. Our Dex implementation
currently supports LDAP, OIDC, SAML and local basic password authentication.

### LDAP
### NOTE: Do not give in plaintext passwords!

```
dex_connectors:
- type: ldap
  id: ldap
  name: LDAP
  host: ldap.example.com:10389
  insecure_no_ssl: true
  bind_dn: cn=admin,dc=example,dc=org
  bind_pw: c2VjcmV0
  usersearch_base_dn: ou=People,dc=example,dc=org
  usersearch_username: mail
  usersearch_id_attr: DN
  usersearch_email_attr: mail
  usersearch_name_attr: cn
  groupsearch_base_dn: ou=Groups,dc=example,dc=org
  groupsearch_filter: (objectClass=groupOfNames)
  groupsearch_user_attr: DN
  groupsearch_group_attr: member
  groupsearch_name_attr: cn
- type: oidc
  id: google
  name: Google
  issuer: https://accounts.google.com
  client_id: 123456789-sa53xywavioajlbb1ssr4dlcec6p3hsa.apps.googleusercontent.com
  client_secret: L3z7S0CokYHxtt87qRlGA0pm
  redirect_uri: https://auth.eccd.local/callback
```

## Clients

Dex will not start without at least one configured client. Clients can be 
configured statically at dex deploy time or dynamically. Erikube will create
a client in the default case for the OIDC dashboard proxy, if it is enabled.

### Static

Static clients are configured using the ansible variable *dex_static_clients* as
in this example:

```
dex_static_clients:
- id: kubernetes-dashboard
  secret: topsecret
  name: "kubernetes"
  redirect_uris:
    - https://dashboard.example.com/oauth2/callback
```

### Dynamic

TBD

## Update/rollback

To rollout a new version of dex simply update the image variable and set the
action variable to 'update'.
