import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './Home';
import Assessments from './Assessments';
import Planner from './Planner';
import NotFound from './NotFound';

const App = () => {
    return (
        <Router>
            <div>
                <Switch>
                    <Route exact path="/" component={Home} />
                    <Route path="/assessments" component={Assessments} />
                    <Route path="/planner" component={Planner} />
                    <Route component={NotFound} />
                </Switch>
            </div>
        </Router>
    );
};

export default App;