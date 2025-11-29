export type Theme = "light" | "dark";

export type Config = {
  baseUrl: string;
  apiKey: string;
  tenantId: string;
};

export type ChatMessage = {
  sender: "user" | "ai";
  text: string;
  time: string;
  context?: string[];
};

export type FollowupCounts = {
  pending: number;
  sent: number;
  failed: number;
};

export type Contact = {
  id: string;
  name?: string;
  phone?: string;
  email?: string;
  status?: string;
};
