import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("trust_token");
  if (token) {
    config.headers = config.headers ?? {};
    (config.headers as any)["X-Trust-Token"] = token;
  }
  return config;
});
