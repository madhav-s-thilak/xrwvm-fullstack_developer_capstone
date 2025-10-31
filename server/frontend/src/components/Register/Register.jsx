import React, { useState } from "react";
import "./Register.css";
import user_icon from "../assets/person.png"
import email_icon from "../assets/email.png"
import password_icon from "../assets/password.png"
import close_icon from "../assets/close.png"

const Register = () => {
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  const gohome = () => {
    window.location.href = window.location.origin;
  }

  const register = async (e) => {
    e.preventDefault();

    let register_url = window.location.origin + "/djangoapp/register";

    const res = await fetch(register_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        "userName": userName,
        "password": password,
        "firstName": firstName,
        "lastName": lastName,
        "email": email
      }),
    });

    const json = await res.json();
    if (json.status) {
      sessionStorage.setItem('username', json.userName);
      window.location.href = window.location.origin;
    }
    else if (json.error === "Already Registered") {
      alert("The user with same username is already registered");
      window.location.href = window.location.origin;
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
      <div className="register_container">
        <div className="header" style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
          <span className="text">SignUp</span>
          <a href="/" onClick={(e) => { e.preventDefault(); gohome(); }}>
            <img style={{ width: "1cm", cursor: "pointer" }} src={close_icon} alt="Close" />
          </a>
        </div>
        <hr />

        <form onSubmit={register}>
          <div className="inputs">
            <div className="input">
              <img src={user_icon} className="img_icon" alt="Username" />
              <input type="text" name="username" placeholder="Username" className="input_field" onChange={(e) => setUserName(e.target.value)} required />
            </div>
            <div className="input">
              <img src={user_icon} className="img_icon" alt="First Name" />
              <input type="text" name="first_name" placeholder="First Name" className="input_field" onChange={(e) => setFirstName(e.target.value)} required />
            </div>

            <div className="input">
              <img src={user_icon} className="img_icon" alt="Last Name" />
              <input type="text" name="last_name" placeholder="Last Name" className="input_field" onChange={(e) => setLastName(e.target.value)} required />
            </div>

            <div className="input">
              <img src={email_icon} className="img_icon" alt="Email" />
              <input type="email" name="email" placeholder="Email" className="input_field" onChange={(e) => setEmail(e.target.value)} required />
            </div>

            <div className="input">
              <img src={password_icon} className="img_icon" alt="Password" />
              <input name="psw" type="password" placeholder="Password" className="input_field" onChange={(e) => setPassword(e.target.value)} required />
            </div>
          </div>

          <div className="submit_panel">
            <input className="submit" type="submit" value="Register" />
          </div>
        </form>
      </div>
    </div>
  );
}

export default Register;
