import { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/")
      .then(res => res.json())
      .then(data => setData(data));
  }, []);

  return <div>{data?.message}</div>;
}

export default App;