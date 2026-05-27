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

export interface Therapy {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export interface Appointment {
  id: number;
  agent_id: number;
  therapist_name: string;
  scheduled_at: string;
  status: string;
  created_at: string;
}

export interface Feedback {
  id: number;
  name: string;
  email: string | null;
  message: string;
  rating: number;
  created_at: string;
}
