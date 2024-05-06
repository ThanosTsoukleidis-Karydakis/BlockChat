import {
  createBrowserRouter,
  RouterProvider,
  Route,
  Outlet,
} from "react-router-dom";
import Home from "./pages/Home"
import Money from "./pages/Money"
import Messages from "./pages/Messages"
import Mining from "./pages/Mining"
import Footer from "./components/Footer"
import Navbar from "./components/Navbar"
import "./styles.scss"

const Layout = () => {
  return (
    <>
      <Navbar />
      <Outlet />
      <Footer />
    </>
  );
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/",
        element: <Home />,
      },
      {
        path: "/money",
        element: <Money />,
      },
      {
        path: "/messages",
        element: <Messages />,
      },
      {
        path: "/mining",
        element: <Mining />,
      },
      ],
  },
]);

function App() {
  return (
    <div className="app">
      <div className="container">
        <RouterProvider router={router} />
      </div>
    </div>
  );
}

export default App;