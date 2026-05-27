import { FC, PropsWithChildren } from "hono/jsx";

export const Main: FC<PropsWithChildren> = ({ children }) => (
  <main aria-label="Main content">{children}</main>
);
