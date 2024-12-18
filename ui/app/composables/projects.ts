export const useProjects = (data?: ProjectsListQuery) => {
  return useApi<ProjectListItem[]>("/execution", {
    query: data,
  });
};

export const useProject = (id: string) => {
  return useApi<Project>(`/execution/${id}`);
};

export const useProjectExperiments = (id: string) => {
  return useApi<ProjectExperiment[]>(`/execution/${id}/experiment`);
};

export const useProjectExperiment = (projectId: string, id: string) => {
  return useApi<ProjectExperiment>(`/execution/${projectId}/experiment/${id}`);
};

export const useProjectCreate = (data: Record<string, any>) => {
  return useApi<{ execution_id: string }>("/execution", {
    method: "POST",
    body: data,
  });
};

export const useProjectExecute = (id: string) => {
  return useApi<{ execution_id: string }>(`/execution/${id}/execute`, {
    method: "POST",
  });
};

export const useProjectValidExperiments = (id: string) => {
  return useApi<ValidExperiment[]>(`/execution/${id}/valid_experiment`);
};

export const useProjectCreateExperiments = (
  id: string,
  data: ValidExperiment[]
) => {
  return useApi<{ execution_id: string }>(`/execution/${id}/experiment`, {
    method: "POST",
    body: data,
  });
};

export const usePresignedUploadUrl = () => {
  return useApi<{
    kb_data: { path: string; presignedurl: string };
    gt_data: { path: string; presignedurl: string };
    uuid: string;
  }>("presignedurl");
};

export const useProjectExperimentQuestionMetrics = (
  id: string,
  experimentId: string
) => {
  return useApi<{ question_metrics: ExperimentQuestionMetric[] }>(
    `/execution/${id}/experiment/${experimentId}/question_metrics`,
    {
      method: "GET",
    }
  );
};
