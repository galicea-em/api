import React from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'

let token = null;
const authorizeUrl = "http://127.0.0.1:5000/login"

const params = {
  scope: ["test-scope"],
  'client_id': "f8fdf5ef-b57a-49e6-b22b-5e8c088e4828",
  'redirect_uri': document.location.href+'callback',
  'response_mode':'fragment'
}

const urlbuilder = (params) => {
  var esc = encodeURIComponent;
  return authorizeUrl+'?'+Object.keys(params)
      .map(k => esc(k) + '=' + esc(params[k]))
      .join('&');
}

const urldecoder = (urlString) => {
  if (urlString.charAt(0) === '#') urlString=urlString.substring(1)
  let pars=urlString.split('&');
  if (pars) {
    let result={}
    pars.map((param) => {
      const [k, v] = param.split('=').map(decodeURIComponent);
      result[k]=v;
      return v 
     })
    return result
  }
  else
    return []
}

const TestImplicit = () => {
  return <div>
    {(!token) && 
    <button onClick={()=>
    {window.open(urlbuilder(params));}}>
      kliknij by pobrać token
    </button>}
    <div>
      reszta strony ....
    </div>
  </div>
}



const Callback = () => {
  if (!token) {
    if (window.location.hash) {
      let hash=urldecoder(window.location.hash)
      token = hash['access_token']    
    } else {
      let search=urldecoder(window.location.search.slice(1))
      token = search['access_token']    
    }
  }


  return <div>
    token={token}
    <br />
    RESZTA strony
    ....
    <br />
    <a href="/">wróć</a>
  </div>
}

export default () => <Router>
  <Switch>
    <Route path="/callback" component={ Callback }/>
    <Route component={ TestImplicit }/>
  </Switch>
</Router>

