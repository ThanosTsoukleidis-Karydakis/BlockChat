import axios from "axios";
import React, { useEffect, useState } from "react";

const Mining = () => {
  const [stake, setStake] = useState(0);
  const [currentStake, setCurrentStake] = useState(0);
  const [stakeChanged, setStakeChanged] = useState(false);
  const [myMinedBlocks, setMyMinedBlocks] = useState([]);
  const [remainingTrans, setRemainingTrans] = useState(-1);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`http://localhost:5001/getStake`);
        console.log("stake", res.data);
        setCurrentStake(res.data.stake);

        const res2 = await axios.get(`http://localhost:5001/getMyMinedBlocks`);
        setMyMinedBlocks(res2.data.myMinedBlocks);
        console.log(res2.data.myMinedBlocks);

        const res3 = await axios.get(
          `http://localhost:5001/getRemainingTransactions`
        );
        console.log(res3.data.number);
        setRemainingTrans(res3.data.number);
      } catch (err) {
        console.log(err);
      }
    };
    fetchData();
  }, [stakeChanged]);

  const handleStake = (e) => {
    setStake(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("stake to be changed: ", stake);
    try {
      let data = {
        type: "stake",
        content: parseInt(stake),
        id: parseInt(-1),
        noFee: true,
      };
      const res = await axios.post(
        "http://localhost:5001/makeTransaction",
        data
      );
      setStakeChanged(!stakeChanged);
      console.log(res.data);
      window.location.reload();
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="mining">
      <h1>
        Congratulations! You have successfully mined {myMinedBlocks.length}{" "}
        blocks!
      </h1>
      <h4>
        Transactions remaining in order for a new block to be mined:{" "}
        {remainingTrans}
      </h4>
      <br></br>
      <br></br>
      <div className="shadowbox">
        <h3>My stake: {currentStake} BCC</h3>
        <div className="stake_info">
          <div>Change stake?: </div>
          <form>
            <input
              required
              type="text"
              placeholder="New Stake"
              name="stake"
              onChange={handleStake}
            />
            <button onClick={handleSubmit}>Submit</button>
          </form>
        </div>
      </div>
      <br></br>
      <br></br>
      <h2>Blocks Mined: </h2>
      <table>
        <thead>
          <tr>
            <th>Location in chain</th>
            <th>Total Fee</th>
          </tr>
        </thead>
        <tbody>
          {myMinedBlocks.map((block, index) => (
            <tr key={index}>
              <td>{block[0]}</td>
              <td>{block[1]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Mining;
