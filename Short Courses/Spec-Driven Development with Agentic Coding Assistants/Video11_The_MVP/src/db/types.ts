export interface Agent {
  id: number;
  name: string;
  model_type: string;
  status: string;
  created_at: string;
}

export interface Ailment {
  id: number;
  name: string;
  description: string;
}
