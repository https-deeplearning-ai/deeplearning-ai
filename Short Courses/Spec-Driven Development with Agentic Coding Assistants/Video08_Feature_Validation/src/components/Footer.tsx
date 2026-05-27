import {FC} from "hono/jsx";

export const Footer: FC = () => (
    <footer>
        <p>&copy; {new Date().getFullYear()} AgentClinic</p>
    </footer>
);