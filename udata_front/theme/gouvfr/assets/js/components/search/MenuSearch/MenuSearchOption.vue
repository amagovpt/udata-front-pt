<template>
  <a class="fr-nav__link unstyled" :href="link">
    <div class="fr-grid-row fr-grid-row--middle">
      <span class="fr-icon--sm align-[-1px] fr-mr-1w" :class="icon" aria-hidden="true"></span>
      <i18n-t keypath="Search {query} in {type}" class="fr-col" tag="div" scope="global" v-if="query">
        <template #query>
          <em>{{query}}</em>
        </template>
        <template #type>
          <strong>{{type}}</strong>
        </template>
      </i18n-t>
      <i18n-t keypath="Start typing to search in X" class="fr-col" tag="div" scope="global" v-else>
        <template #type>
          <strong>{{type}}</strong>
        </template>
      </i18n-t>
      <div aria-hidden="true" class="fr-col-auto">
        <span class="fr-icon-arrow-right-s-line fr-icon--sm" aria-hidden="true"></span>
      </div>
    </div>
  </a>
</template>

<script setup lang="ts">
defineProps<{
  icon: string,
  query: string,
  link: string,
  type: string
}>();
</script>
