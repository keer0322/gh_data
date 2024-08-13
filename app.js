import logo from './Logo.svg';
import './App.css';
import { useState, useEffect } from 'react';

function App() {
  const [name, setName] = useState([]);

  useEffect(() => {
    names();
  }, []);

  const names = async () => {
    const delegateBody = { filterType: "Delegate" }; // Fixed the object syntax
    const inputHeaders = {
      'x-api-key': 'test',
      'Content-Type': 'application/json',
    };
    const paramHeaders = {
      method: 'POST',
      headers: inputHeaders,
      body: JSON.stringify(delegateBody),
    };

    try {
      const response = await fetch('https://app.harness.io/ng/api/delegate-setup/listDelegates?accountIdentifier=test', paramHeaders);
      const isJson = response.headers.get('content-type')?.includes('application/json');
      const data = isJson ? await response.json() : null;

      if (!response.ok) {
        const error = (data && data.message) || response.status;
        return Promise.reject(error);
      }

      setName(data);
    } catch (error) {
      console.error('There was an error!', error);
    }
  };

  return (
    <div className="Delegates">
      <h1 className="DelegateName">Delegates List</h1>
      <ol className="list-group list-group-numbered">
        {name.map((data) => (
          <li className="list-group-item" key={data.id}>{data.title}</li>
        ))}
      </ol>
    </div>
  );
}

export default App;
