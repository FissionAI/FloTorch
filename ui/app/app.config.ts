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
          'w-full h-6 flex border my- border-gray-300 rounded'
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
  },
});
