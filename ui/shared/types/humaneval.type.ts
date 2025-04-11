import { z } from "zod";

export const HumanEvalSchema = z.object({
    message: z.string(),
});

export type HumanEval = z.infer<typeof HumanEvalSchema>;