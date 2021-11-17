import './App.css';
import Iframe from './components/iframe';
import Navbar from './components/navbar';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <Navbar />
      </header>
      <section className="content">
        {/* <h1>Participation</h1> */}
        <Iframe></Iframe>     
      </section>
    </div>
  );
}

export default App;
