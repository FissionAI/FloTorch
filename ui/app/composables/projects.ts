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


export const useProjectValidExperiments = (id: string)  => {
  return useApi<{message: string}>(`/execution/${id}/valid_experiment`);
};

export const useProjectValidExperimentsByPoll = (id: string) => {
  // required to access the response.code, so that i have used useApi.raw below
  return useApi.raw(`/execution/${id}/valid_experiment/poll`);
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

// export const usePresignedUploadUrl = () => {
//   return useApi<{
//     kb_data: { path: string; presignedurl: string };
//     gt_data: { path: string; presignedurl: string };
//     uuid: string;
//   }>("presignedurl");
// };

export const usePresignedUploadUrl = (uuid: string) => {
  return useApi<{
    gt_data: { path: string; presignedurl: string };
  }>("presignedurl", {
    method: "POST",
    body: { unique_id: uuid }
  });
};

export const usePresignedUploadUrlKb = (id: string, files: string[]) => {
  return useApi("presigned_url_kb", {
    method: "POST",
    body: {
      unique_id: id,
      files: files
    }
  });
}

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
