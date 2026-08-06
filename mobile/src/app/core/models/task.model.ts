export enum TaskStatus {
  Pendiente = 'PENDIENTE',
  Completada = 'COMPLETADA',
  Pospuesta = 'POSPUESTA',
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  due_date: string | null;
  created_at: string;
  updated_at: string;
  created_by: string;
  is_expiring: boolean;
}

export interface CreateTaskPayload {
  title: string;
  description?: string;
  status?: TaskStatus;
  due_date?: string | null;
}

export type UpdateTaskPayload = Partial<CreateTaskPayload>;

export type TaskFilter = 'all' | 'pending' | 'completed' | 'expiring';

export const STATUS_LABELS: Record<TaskStatus, string> = {
  [TaskStatus.Pendiente]: 'Pendiente',
  [TaskStatus.Completada]: 'Completada',
  [TaskStatus.Pospuesta]: 'Pospuesta',
};
