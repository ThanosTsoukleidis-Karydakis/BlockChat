import axios from "axios";
import React, { useState } from "react";
import { Link } from "react-router-dom";

const Home = () => {
  const [idReceiver, setIdReceiver] = useState(-1);
  const [message, setMessage] = useState("");
  const [idReceiverTrans, setIdReceiverTrans] = useState(-1);
  const [amount, setAmount] = useState(0);

  const handleMessage = (e) => {
    setMessage(e.target.value);
  };

  const handleReceiver = (e) => {
    setIdReceiver(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(idReceiver, message);
    try {
      let data = {
        type: "message",
        content: message,
        id: parseInt(idReceiver),
        noFee: false,
      };
      const res = await axios.post(
        "http://localhost:5001/makeTransaction",
        data
      );
      console.log(res.data);
      window.location.reload();
      setMessage("");
      setIdReceiver(-1);
    } catch (err) {
      console.log(err);
    }
  };

  const handleAmount = (e) => {
    setAmount(e.target.value);
  };

  const handleReceiverTrans = (e) => {
    setIdReceiverTrans(e.target.value);
  };

  const handleSubmitTrans = async (e) => {
    e.preventDefault();
    console.log(idReceiver, message);
    try {
      let data = {
        type: "coins",
        content: parseInt(amount),
        id: parseInt(idReceiverTrans),
        noFee: false,
      };
      const res = await axios.post(
        "http://localhost:5001/makeTransaction",
        data
      );
      console.log(res.data);
      window.location.reload();
      setAmount(0);
      setIdReceiverTrans(-1);
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="home">
      <div className="container">
        <div className="forms">
          <form className="messageForm">
            <h2>Send a message:</h2>
            <input
              required
              type="text"
              placeholder="Receiver"
              name="receiver"
              onChange={handleReceiver}
            />
            <input
              required
              type="text"
              placeholder="Message"
              name="message"
              onChange={handleMessage}
            />
            <button onClick={handleSubmit}>Send Message</button>
            <section hidden>Your message has been sent!</section>
          </form>

          <form className="amountForm">
            <h2>Send money:</h2>
            <input
              required
              type="text"
              placeholder="Receiver"
              name="receiver"
              onChange={handleReceiverTrans}
            />
            <input
              required
              type="text"
              placeholder="Amount"
              name="amount"
              onChange={handleAmount}
            />
            <button onClick={handleSubmitTrans}>Transfer Money</button>
            <section hidden>The given amount has been sent!</section>
          </form>
        </div>
        <br></br>
        <br></br>
        <br></br>
        <div className="buttons">
          <Link to="/messages">
            <button className="listMess">Show Messages</button>
          </Link>
          <Link to="/money">
            <button className="listMoney">Show Money Transfers</button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
