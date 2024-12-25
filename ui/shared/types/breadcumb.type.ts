export interface BreadcrumbItem {
  label: string;
  icon?: string;
  to: string;
  disabled?: boolean;
}

export interface CustomLabels {
  [key: string]: string;
}
