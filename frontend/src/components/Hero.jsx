import Navbar from "./Navbar";
import TripSearchBar from "./TripSearchBar";
import { Sparkles } from "lucide-react";

const Hero = () => {

  return (

    <div className="hero">

      <Navbar />

      <div className="hero-overlay"/>

      <div className="hero-content">

        <div className="badge">

          <Sparkles size={14}/>

          AI TRAVEL ARCHITECT

        </div>

        <h1>

          Experience the
          <br/>
          Extraordinary

        </h1>

        <p>

          Your next journey is just one click away.

        </p>

        <TripSearchBar/>

      </div>

    </div>

  );

};

export default Hero;