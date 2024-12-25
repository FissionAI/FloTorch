<script setup lang="ts">
import { keepPreviousData, useQuery } from "@tanstack/vue-query"

const page = useRouteQuery("page", 1, { transform: Number })
const limit = useRouteQuery("limit", 20, { transform: Number })
const search = useRouteQuery("search", undefined)

const { data: projects, isLoading } = useQuery({
  queryKey: ["projects", page, limit, search],
  queryFn: () =>
    useProjects({
      page: page.value,
      limit: limit.value,
      search: search.value,
    }),
  placeholderData: keepPreviousData,
});

useHead({
  title: "Projects",
})
</script>

<template>
  <Page title="Projects">
    <Breadcumb />
    <template #actions>
      <ProjectUploadConfigButton />
      <UButton
        icon="i-lucide-plus"
        :to="{ name: 'projects-create' }"
        label="Create Project"
      />
    </template>
    <UCard>
      <div v-if="isLoading" class="flex justify-center items-center h-24">
        Loading projects...
      </div>
      <ProjectList
        v-else-if="projects && projects.length"
        :projects="projects"
        :is-loading="isLoading"
      />
      <div v-else class="flex justify-center items-center h-24">
        No projects found
      </div>
    </UCard>
  </Page>
</template>
