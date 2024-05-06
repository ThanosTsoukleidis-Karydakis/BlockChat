import React, { useState } from "react";
import { useEffect } from "react";
import Logo from "../img/logo.png";
import { Link } from "react-router-dom";
import axios from "axios";

const Navbar = () => {
  const [balance, setBalance] = useState();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`http://localhost:5001/getBalance`);
        console.log(res.data);
        setBalance(res.data.balance);
      } catch (err) {
        console.log(err);
      }
    };
    fetchData();
  }, []);
  return (
    <div className="navbar">
      <div className="container">
        <div className="logo">
          <Link to="/">
            <img src={Logo} alt="" />
          </Link>
        </div>
        <div className="to_the_right">
          <div class="balance-box">
            <span class="balance-text">My Balance: {balance} BCC</span>
          </div>
          <Link to="/mining">
            <button class="mining">Mining</button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
