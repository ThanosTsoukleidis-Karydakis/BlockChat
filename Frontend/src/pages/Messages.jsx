import React, { useState } from "react";
import { useEffect } from "react";
import Logo from "../img/logo.png";
import { Link } from "react-router-dom";
import axios from "axios";

const Money = () => {
  const [outgoingMessages, setOutgoingMessages] = useState([]);
  const [ingoingMessages, setIngoingMessages] = useState([]);
  const [ButtonPressed, setButtonPressed] = useState(0);

  const handleButtonClick = () => {
    let helper = ButtonPressed + 1;
    setButtonPressed(helper);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(
          `http://localhost:5001/getOutgoingMessages`
        );
        console.log(res.data);
        setOutgoingMessages(res.data.outGoingTransactions);
      } catch (err) {
        console.log(err);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`http://localhost:5001/getIngoingMessages`);
        console.log(res.data);
        setIngoingMessages(res.data.inGoingTransactions);
      } catch (err) {
        console.log(err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="money">
      <br />
      <br />
      {ButtonPressed % 2 === 0 ? (
        <div>
          <h3>Outgoing Messages</h3>
          <div className="buttons">
            <button onClick={handleButtonClick}>Show Ingoing Messages</button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Receiver</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {outgoingMessages.map((transfer, index) => (
                <tr key={index}>
                  <td>{transfer.receiver_address}</td>
                  <td>{transfer.content}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div>
          <h3>Ingoing Messages</h3>
          <div className="buttons">
            <button onClick={handleButtonClick}>Show Outgoing Messages</button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Sender</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {ingoingMessages.map((transfer, index) => (
                <tr key={index}>
                  <td>{transfer.sender_address}</td>
                  <td>{transfer.content}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Money;
