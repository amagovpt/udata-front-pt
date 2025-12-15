import { createApp } from "vue";
import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router';
import { setupComponents } from "@datagouv/components/ts";

import "./dsfr.ts";
// @ts-ignore
import "@gouvfr/dsfr/dist/dsfr/dsfr.module";

import i18n from "./i18n.ts";
import { admin_root, schema_documentation_url, schema_validata_url, tabular_api_url, tabular_page_size, title, sentry } from "./config.ts";
import Api from "./plugins/api.ts";
import Auth from "./plugins/auth.ts";
// Sentry is now loaded dynamically only when DSN is configured

setupComponents({
  admin_root,
  default_lang: i18n.global.locale.value,
  only_locales: i18n.global.locale.value,
  schema_documentation_url,
  schema_validata_url,
  show_copy_resource_permalink: true,
  tabular_api_url,
  tabular_page_size,
  title,
});

const routes: Array<RouteRecordRaw> = [
  {
    path: '/me',
    children: [
      { path: '', component: Me, name: "me" },
      { path: 'datasets', component: Datasets, name: "me-datasets" },
      { path: 'reuses', component: Reuses, name: "me-reuses" },
      { path: 'community-resources', component: CommunityResources, name: "me-community-resources" },
    ]
  },
  {
    path: '/organizations/:oid',
    children: [
      { path: 'datasets', component: Datasets, props: true, name: "organization-datasets" },
      { path: 'reuses', component: Reuses, props: true, name: "organization-reuses" },
      { path: 'discussions', component: Discussions, props: true, name: "organization-discussions" },
      { path: 'members', component: Members, props: true, name: "organization-members" },
      { path: 'harvesters', component: Harvesters, props: true, name: "organization-harvesters" },
      { path: 'community-resources', component: CommunityResources, props: true, name: "organization-community-resources" },
      { path: 'profile', component: Profile, props: true, name: "organization-profile" },
    ],
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

const app = createApp(Admin);

// Only load and initialize Sentry if DSN is configured
if (sentry.dsn) {
  import("./sentry.ts").then(({ default: InitSentry }) => {
    InitSentry(app).catch((error: unknown) => {
      console.warn('Failed to initialize Sentry:', error);
    });
  }).catch((error: unknown) => {
    console.warn('Failed to load Sentry:', error);
  });
}

app.use(Api);
app.use(Auth);
app.use(i18n);
app.use(router);

app.mount("#admin");
// @ts-ignore dsfr is added by @gouvfr/dsfr
globalThis.dsfr.start();
console.log("JS is injected !");
