
import logo from './logo.svg';
import './App.css';
import AudioRecorder from './AudioRecorder';
import RoleQuestions from './RoleQuestions';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Interview Prep App</h1>
        <RoleQuestions />
        <AudioRecorder />
      </header>
    </div>
  );
}

export default App;
