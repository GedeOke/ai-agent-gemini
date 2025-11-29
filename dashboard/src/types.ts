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
};
