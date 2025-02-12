export default defineAppConfig({
  ui: {
    colors: {
      // primary: "orange",
    },
    form: {
      base: "space-y-3",
    },
    input: {
      slots: {
        root: "w-full",
      },
      defaultVariants: {
        // @ts-expect-error type inference
        size: "xl",
      },
    },
    selectMenu: {
      defaultVariants: {
        // @ts-expect-error type inference
        size: "xl",
      },
      slots : {
        group: 'p-1 isolate-custom',
        item : [
          'custom-options-group w-full'
        ],
        input: 'h-6',
      }
    },
    inputNumber: {
      slots: {
        root: "w-full",
      },
    },
    table: {
      slots: {
        td: "!whitespace-normal",
      },
    },
    tabs: {
      slots : {
        root : "gap-2",
        list: "custom-tab-list-group",
        indicator : "h-10px custom-tab-indicator",
        trigger : ['custom-tabs-trigger'],
        content : "focus-outline"
      }
    }
  },
});
