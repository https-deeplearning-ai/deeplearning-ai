import {FC, PropsWithChildren} from "hono/jsx";

export const Main: FC<PropsWithChildren> = ({children}) => (
    <main>{children}</main>
);