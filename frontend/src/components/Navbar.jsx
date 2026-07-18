import {
  Plane,
  Bed,
  Mountain,
  Sparkles,
  PlaneTakeoff,
} from "lucide-react";

const Navbar = () => {
  return (
    <nav className="navbar">

      <div className="logo">

        <div className="logo-icon">
          <PlaneTakeoff size={24}/>
        </div>

        <span>SARTHI.AI</span>

      </div>

      <div className="nav-links">

        <a href="#">
          <Plane size={18}/>
          Flights
        </a>

        <a href="#">
          <Bed size={18}/>
          Stays
        </a>

        <a href="#">
          <Mountain size={18}/>
          Experiences
        </a>

        <a href="#">
          <Sparkles size={18}/>
          AI Planner
        </a>

      </div>

    </nav>
  );
};

export default Navbar;