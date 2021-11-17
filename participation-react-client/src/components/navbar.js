export default function Navbar() {
    return (
        <div className="navbar">
            <div className="logo"><img alt="Logo participation" src="https://participation-in.eu/media/participation-logo-w.png"></img></div>
            <input type="checkbox" id="nav-toggle" className="nav-toggle" />
            <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/">About</a></li>
                    <li><a href="/">Blog</a></li>
                    <li><a href="/">Contact</a></li>
                </ul>
            </nav>
            <label htmlFor="nav-toggle" className="nav-toggle-label">
                <span></span>
            </label>
        </div>
    )
}