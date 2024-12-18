<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';
const UButton = resolveComponent('UButton')



defineProps<{
  projects: ProjectListItem[]
  isLoading: boolean
}>()

const columns = ref<TableColumn<ProjectListItem>[]>([
  {
    header: "ID",
    accessorKey: "id"
  },
  {
    header: "Name",
    accessorKey: "name"
  },
  {
    header: "Region",
    accessorKey: "region"
  },
  {
    accessorKey: "status",
    id: "status",
    enableSorting: true,
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Status',
        icon: isSorted
          ? isSorted === 'asc'
            ? 'i-lucide-arrow-up-narrow-wide'
            : 'i-lucide-arrow-down-wide-narrow'
          : 'i-lucide-arrow-up-down',
        class: '-mx-2.5',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
      })
    }
  },
  {
    accessorKey: "date",
    id: "date",
    enableSorting: true,
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Date',
        icon: isSorted
          ? isSorted === 'asc'
            ? 'i-lucide-arrow-up-narrow-wide'
            : 'i-lucide-arrow-down-wide-narrow'
          : 'i-lucide-arrow-up-down',
        class: '-mx-2.5',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
      })
    }
  }
])

const sorting = ref([
  {
    id: "date",
    desc: true
  },
  {
    id: "status",
    desc: false
  }
])

</script>

<template>
  <UTable v-model:sorting="sorting" :columns="columns" :data="projects">
    <template #id-cell="{ row }">
      <NuxtLink :to="{ name: 'projects-id', params: { id: row.original.id } }" class="text-blue-500 hover:underline">
        {{ row.original.id }}
      </NuxtLink>
    </template>
    <template #name-cell="{ row }">
      <NuxtLink :to="{ name: 'projects-id', params: { id: row.original.id } }" class="text-blue-500 hover:underline">
        {{ row.original.name || "Not available" }}
      </NuxtLink>
    </template>
    <template #status-cell="{ row }">
      <UBadge variant="subtle" :color="useProjectStatusColor(row.original.status)">
        <template #leading>
          <UIcon :name="useProjectStatusIcon(row.original.status)" />
        </template>
        {{ useHumanProjectStatus(row.original.status) }}
      </UBadge>
    </template>
    <template #date-cell="{ row }">
      {{ useHumanDateTime(row.original.date.toString()) }}
    </template>
  </UTable>
</template>
