import React, { useState } from "react";
import { useEffect } from "react";
import Logo from "../img/logo.png";
import { Link } from "react-router-dom";
import axios from "axios";

const Money = () => {
  const [outgoingTransfers, setOutgoingTransfers] = useState([]);
  const [ingoingTransfers, setIngoingTransfers] = useState([]);
  const [ButtonPressed, setButtonPressed] = useState(0);

  const handleButtonClick = () => {
    let helper = ButtonPressed + 1;
    setButtonPressed(helper);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(
          `http://localhost:5001/getOutgoingMoneyTransfers`
        );
        console.log(res.data);
        setOutgoingTransfers(res.data.outGoingTransactions);
      } catch (err) {
        console.log(err);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(
          `http://localhost:5001/getIngoingMoneyTransfers`
        );
        console.log(res.data);
        setIngoingTransfers(res.data.inGoingTransactions);
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
          <h3>Outgoing Money Transfers</h3>
          <div className="buttons">
            <button onClick={handleButtonClick}>
              Show Ingoing Money Transfers
            </button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Receiver</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {outgoingTransfers.map((transfer, index) => (
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
          <h3>Ingoing Money Transfers</h3>
          <div className="buttons">
            <button onClick={handleButtonClick}>
              Show Outgoing Money Transfers
            </button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Sender</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {ingoingTransfers.map((transfer, index) => (
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
