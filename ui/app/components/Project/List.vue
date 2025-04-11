<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
const UButton = resolveComponent("UButton");

defineProps<{
  projects: ProjectListItem[];
  isLoading: boolean;
}>();

const columns = ref<TableColumn<ProjectListItem>[]>([
  {
    accessorKey: "id",
    id: "id",
    enableSorting: true,
    header: ({ column }) => {
      const isSorted = column.getIsSorted();

      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          label: "Id",
          trailingIcon: isSorted
            ? isSorted === "asc"
              ? "i-lsicon:triangle-up-filled"
              : "i-lsicon:triangle-down-filled"
            : "i-lsicon:triangle-down-outline",
         class:"-mx-2.5 focus:font-bold hover:font-bold",
          onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.id ?? 0;
      const b = rowB.original.id ?? 0;
      return a.localeCompare(b);
    },
  },
  {
    accessorKey: "name",
    id: "name",
    enableSorting: true,
    header: ({ column }) => {
      const isSorted = column.getIsSorted();

      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          label: "Name",
          trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
       class:"-mx-2.5 focus:font-bold hover:font-bold",
          onClick: () => column.toggleSorting(),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    label: 'Name',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.name ?? 0;
      const b = rowB.original.name ?? 0;
      return a.localeCompare(b);
    },
  },
  {
    accessorKey: "region",
    id: "region",
    enableSorting: true,
    header: ({ column }) => {
      const isSorted = column.getIsSorted();

      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          label: "Region",
          trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
       class:"-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
  },
  {
    accessorKey: "status",
    id: "status",
    enableSorting: true,
    header: ({ column }) => {
      const isSorted = column.getIsSorted();

      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          label: "Status",
          trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
       class:"-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
  },
  {
    accessorKey: "date",
    id: "date",
    enableSorting: true,
    header: ({ column }) => {
      const isSorted = column.getIsSorted();

      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Date",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
       class:"-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(),
      });
    },
  },
]);

const sorting = ref([
  {
    id: "id",
    asc: true,
  },
]);
</script>

<template>
  <UTable class="h-[calc(100vh-430px)]" sticky v-model:sorting="sorting" :columns="columns" :data="projects">
    <template #id-cell="{ row }">
      <NuxtLink
        :to="{ name: 'projects-id', params: { id: row.original.id } }"
        class="text-blue-500 hover:text-black hover:underline"
      >
        {{ row.original.id }}
      </NuxtLink>
    </template>
    <template #name-cell="{ row }">
      {{ row.original.name || "Not available" }}
    </template>
    <template #status-cell="{ row }">
      <!-- <UBadge
        variant="subtle"
        :color="useProjectStatusColor(row.original.status)"
      > -->
      <div :class="`${useProjectBadgeColor(row.original.status)}-badge`" class="flex items-center gap-2">
        <UIcon :name="useProjectBadgeIcon(row.original.status)" />
        {{ useHumanProjectStatus(row.original.status) }}
      </div>
        <!-- <template #leading>
          <UIcon :name="useProjectStatusIcon(row.original.status)" />
        </template>
        {{ useHumanProjectStatus(row.original.status) }} -->
      <!-- </UBadge> -->
    </template>
    <template #date-cell="{ row }">
      {{ useHumanDateTime(row.original.date.toString()) }}
    </template>
  </UTable>
</template>
