"use client";
import { useEffect, useMemo, useState } from "react";

type Mode = "apartments" | "vehicles";
type Listing = {
  id: number;
  mode: Mode;
  title: string;
  detail: string;
  place: string;
  image: string;
  price: number;
  total: number;
  period: string;
  rating: string;
  provider: string;
  tags: string[];
  badge: string;
  fees: string;
  xy: [number, number];
};

const fallbackData: Listing[] = [
  { id: 1, mode: "apartments", title: "The Maxwell at Frisco", detail: "1 bed · 1 bath · 742 sq ft", place: "Warren Pkwy, Frisco · 1.8 mi", image: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267d?auto=format&fit=crop&w=900&q=85", price: 1485, total: 1554, period: "/mo", rating: "4.8", provider: "RentCafe", tags: ["Gym", "Pool", "Parking"], badge: "Best overall", fees: "$69 mandatory fees included", xy: [23, 38] },
  { id: 2, mode: "apartments", title: "Cypress Lake at Stonebriar", detail: "1 bed · 1 bath · 785 sq ft", place: "Warren Pkwy, Frisco · 2.3 mi", image: "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=900&q=85", price: 1520, total: 1580, period: "/mo", rating: "4.6", provider: "Apartments.com", tags: ["Pet friendly", "Garage", "Pool"], badge: "1 month free", fees: "$60 monthly fees included", xy: [61, 25] },
  { id: 3, mode: "apartments", title: "Frisco Square Lofts", detail: "Studio · 1 bath · 611 sq ft", place: "Hickory St, Frisco · 0.7 mi", image: "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=900&q=85", price: 1325, total: 1407, period: "/mo", rating: "4.5", provider: "Zillow", tags: ["Walkable", "Coworking", "Parking"], badge: "Lowest total", fees: "$82 mandatory fees included", xy: [43, 59] },
  { id: 4, mode: "vehicles", title: "Toyota RAV4 or similar", detail: "Compact SUV · 5 seats · 3 bags", place: "DFW Airport · At terminal", image: "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?auto=format&fit=crop&w=900&q=85", price: 48, total: 326, period: "/day", rating: "4.7", provider: "Budget", tags: ["Unlimited miles", "Free cancellation", "Automatic"], badge: "Best value", fees: "$86 taxes & fees included · 5 days", xy: [24, 42] },
  { id: 5, mode: "vehicles", title: "Nissan Rogue or similar", detail: "Midsize SUV · 5 seats · 4 bags", place: "DFW Airport · At terminal", image: "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=900&q=85", price: 51, total: 349, period: "/day", rating: "4.8", provider: "Enterprise", tags: ["Unlimited miles", "Pay at pickup", "Automatic"], badge: "Top rated", fees: "$94 taxes & fees included · 5 days", xy: [60, 28] },
  { id: 6, mode: "vehicles", title: "Hyundai Elantra or similar", detail: "Midsize · 5 seats · 2 bags", place: "Frisco Downtown · 1.2 mi", image: "https://images.unsplash.com/photo-1553440569-bcc63803a83d?auto=format&fit=crop&w=900&q=85", price: 39, total: 267, period: "/day", rating: "4.5", provider: "Hertz", tags: ["Unlimited miles", "Free cancellation", "Automatic"], badge: "Lowest total", fees: "$72 taxes & fees included · 5 days", xy: [42, 61] },
];

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const I = ({ n, fill = false }: { n: string; fill?: boolean }) => (
  <svg
    viewBox="0 0 24 24"
    fill={fill ? "currentColor" : "none"}
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    {n === "spark" ? (
      <path d="m12 3 1.5 4.3L18 9l-4.5 1.7L12 15l-1.5-4.3L6 9l4.5-1.7L12 3ZM5 15l.8 2.2L8 18l-2.2.8L5 21l-.8-2.2L2 18l2.2-.8L5 15Z" />
    ) : n === "pin" ? (
      <>
        <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" />
        <circle cx="12" cy="10" r="2.5" />
      </>
    ) : n === "heart" ? (
      <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.5a5.5 5.5 0 0 0 1-8.9Z" />
    ) : (
      <>
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-4-4" />
      </>
    )}
  </svg>
);

export default function Home() {
  const [mode, setMode] = useState<Mode>("apartments");
  const [place, setPlace] = useState("Frisco, TX");
  const [saved, setSaved] = useState<number[]>([3]);
  const [compare, setCompare] = useState<number[]>([]);
  const [map, setMap] = useState(true);
  const [sort, setSort] = useState("Recommended");
  const [ai, setAi] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [note, setNote] = useState("I found 3 strong matches and included mandatory fees in every total.");
  const [listings, setListings] = useState<Listing[]>(fallbackData);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      const params = new URLSearchParams({ mode });
      const trimmedPlace = place.trim();
      if (trimmedPlace) params.set("q", trimmedPlace);

      try {
        const res = await fetch(`${API_BASE_URL}/api/listings?${params.toString()}`, { cache: "no-store" });
        if (!res.ok) throw new Error("Failed to load listings");
        const data: Listing[] = await res.json();
        if (alive && Array.isArray(data)) {
          setListings(data.length ? data : fallbackData.filter((d) => d.mode === mode));
        }
      } catch {
        if (alive) {
          const fallback = fallbackData.filter((d) => d.mode === mode);
          setListings(trimmedPlace
            ? fallback.filter((d) => [d.title, d.detail, d.place, d.provider, ...d.tags].join(" ").toLowerCase().includes(trimmedPlace.toLowerCase()))
            : fallback);
        }
      }
    };

    void load();
    return () => {
      alive = false;
    };
  }, [mode, place]);

  const normalizedPlace = place.trim().toLowerCase();

  const results = useMemo(() => {
    let x = listings.filter((d) => d.mode === mode);

    if (normalizedPlace) {
      const query = normalizedPlace;
      x = x.filter((d) => {
        const haystacks = [d.title, d.detail, d.place, d.provider].join(" ").toLowerCase();
        return haystacks.includes(query);
      });
    }

    if (sort === "Lowest total") return [...x].sort((a, b) => a.total - b.total);
    if (sort === "Highest rated") return [...x].sort((a, b) => Number(b.rating) - Number(a.rating));
    return x;
  }, [listings, mode, normalizedPlace, sort]);

  const change = (m: Mode) => {
    setMode(m);
    setPlace(m === "apartments" ? "Frisco, TX" : "DFW Airport");
    setNote(
      m === "apartments"
        ? "I found 3 strong matches and included mandatory fees in every total."
        : "I compared the full 5-day trip cost—not just the advertised daily price."
    );
  };

  const ask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    const q = prompt.toLowerCase();
    if (/car|suv|vehicle/.test(q)) change("vehicles");
    if (/apartment|bedroom|studio/.test(q)) change("apartments");
    setNote(`Filters updated from: “${prompt}”`);
    setPrompt("");
    setAi(false);
  };

  return (
    <main>
      <header>
        <a className="brand">
          <b>
            <I n="spark" />
          </b>
          RentWise <em>AI</em>
        </a>
        <nav>
          <a className="active">Search</a>
          <a>
            Saved <small>{saved.length}</small>
          </a>
          <a>Trips</a>
        </nav>
        <button className="list-rental">List your rental</button>
        <button className="avatar">MC</button>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <I n="spark" /> AI rental search
          </span>
          <h1>
            One search. Every rental.
            <br />
            <i>The real best price.</i>
          </h1>
          <p>Compare apartments and vehicles with every mandatory fee included.</p>
        </div>

        <div className="tabs">
          <button className={mode === "apartments" ? "on" : ""} onClick={() => change("apartments")}>
            ⌂ Apartments
          </button>
          <button className={mode === "vehicles" ? "on" : ""} onClick={() => change("vehicles")}>
            ◇ Vehicles
          </button>
        </div>

        <div className="searchbar">
          <label>
            <small>WHERE</small>
            <span>
              <I n="pin" />
              <input value={place} onChange={(e) => setPlace(e.target.value)} />
            </span>
          </label>
          {mode === "apartments" ? (
            <>
              <button>
                <small>MOVE-IN</small>
                <b>Sep 1, 2026</b>
              </button>
              <button>
                <small>LEASE</small>
                <b>12 months</b>
              </button>
              <button>
                <small>BEDROOMS</small>
                <b>Studio or 1 bed</b>
              </button>
            </>
          ) : (
            <>
              <button>
                <small>PICK-UP</small>
                <b>Sep 10 · 10:00 AM</b>
              </button>
              <button>
                <small>DROP-OFF</small>
                <b>Sep 15 · 10:00 AM</b>
              </button>
              <button>
                <small>DRIVER</small>
                <b>Age 26+</b>
              </button>
            </>
          )}
          <button
            className="go"
            onClick={() => {
              const nextPlace = place.trim() || (mode === "apartments" ? "Frisco, TX" : "DFW Airport");
              setPlace(nextPlace);
              setNote(`Updated results near ${nextPlace}. Known mandatory fees are included.`);
            }}
          >
            <I n="search" /> Search
          </button>
        </div>

        <button className="ask" onClick={() => setAi(true)}>
          <b>
            <I n="spark" />
          </b>
          <span>
            <strong>Describe what you need</strong>
            <small>“A quiet 1-bedroom under $1,600 with parking…”</small>
          </span>
          <kbd>⌘ K</kbd>
        </button>
      </section>

      <section className="work">
        <aside>
          <div className="filter-head">
            <h2>Filters</h2>
            <button>Reset</button>
          </div>

          <div className="filter">
            <h3>True {mode === "apartments" ? "monthly" : "trip"} cost <i>?</i></h3>
            <div className="prices">
              <span>
                <small>Minimum</small>
                <b>$0</b>
              </span>
              <em>–</em>
              <span>
                <small>Maximum</small>
                <b>${mode === "apartments" ? "1,700" : "500"}</b>
              </span>
            </div>
            <input type="range" defaultValue="55" />
            <div className="scale">
              <small>$0</small>
              <small>${mode === "apartments" ? "3,000+" : "1,000+"}</small>
            </div>
          </div>

          <div className="filter">
            <h3>{mode === "apartments" ? "Bedrooms" : "Vehicle type"}</h3>
            <div className="chips">
              {(mode === "apartments" ? ["Studio", "1", "2", "3+"] : ["Car", "SUV", "Van", "Truck"]).map((x, i) => (
                <button className={i === 1 ? "on" : ""} key={x}>
                  {x}
                </button>
              ))}
            </div>
          </div>

          <div className="filter">
            <h3>Must-haves</h3>
            {(mode === "apartments"
              ? ["In-unit laundry", "Parking included", "Pet friendly", "Pool or gym"]
              : ["Unlimited mileage", "Free cancellation", "Automatic", "Pay at pickup"]
            ).map((x, i) => (
              <label key={x}>
                <input type="checkbox" defaultChecked={i < 2} />
                <span>✓</span>
                {x}
              </label>
            ))}
          </div>

          <div className="filter">
            <h3>Distance</h3>
            <select>
              <option>Within 5 miles</option>
              <option>Within 10 miles</option>
              <option>Within 25 miles</option>
            </select>
          </div>

          <button className="all">
            ☷ All filters <b>2</b>
          </button>
        </aside>

        <div className="results">
          <div className="results-head">
            <div>
              <h2>
                {results.length} rentals near {place}
              </h2>
              <p>
                <i /> Prices checked 4 minutes ago
              </p>
            </div>
            <div>
              <button onClick={() => setMap(false)} className={!map ? "on" : ""}>
                ☷ List
              </button>
              <button onClick={() => setMap(true)} className={map ? "on" : ""}>
                ⌖ Map
              </button>
              <select value={sort} onChange={(e) => setSort(e.target.value)}>
                <option>Recommended</option>
                <option>Lowest total</option>
                <option>Highest rated</option>
              </select>
            </div>
          </div>

          <div className="insight">
            <b>
              <I n="spark" />
            </b>
            <span>
              <strong>RentWise AI insight</strong>
              <p>{note}</p>
            </span>
            <button onClick={() => setAi(true)}>Refine with AI →</button>
          </div>

          <div className={`content ${!map ? "wide" : ""}`}>
            <div className="cards">
              {results.map((d) => (
                <article key={d.id}>
                  <div className="photo" style={{ backgroundImage: `url(${d.image})` }}>
                    <span>{d.badge}</span>
                    <button
                      onClick={() =>
                        setSaved((s) => (s.includes(d.id) ? s.filter((x) => x !== d.id) : [...s, d.id]))
                      }
                      className={saved.includes(d.id) ? "saved" : ""}
                    >
                      <I n="heart" fill={saved.includes(d.id)} />
                    </button>
                    <small>▧ 8</small>
                  </div>

                  <div className="card-body">
                    <div className="card-top">
                      <div>
                        <small>{d.provider}</small>
                        <h3>{d.title}</h3>
                        <p>{d.detail}</p>
                      </div>
                      <b>
                        ★ {d.rating}
                        <small> verified</small>
                      </b>
                    </div>

                    <p className="location">
                      <I n="pin" />
                      {d.place}
                    </p>

                    <div className="tags">
                      {d.tags.map((x) => (
                        <span key={x}>{x}</span>
                      ))}
                    </div>

                    <div className="cost">
                      <label>
                        <input
                          type="checkbox"
                          checked={compare.includes(d.id)}
                          onChange={() =>
                            setCompare((c) =>
                              c.includes(d.id) ? c.filter((x) => x !== d.id) : c.length < 3 ? [...c, d.id] : c
                            )
                          }
                        />
                        Compare
                      </label>

                      <div>
                        <small>
                          from <s>${d.price + (mode === "apartments" ? 110 : 12)}</s>
                        </small>
                        <p>
                          <strong>${d.price.toLocaleString()}</strong>
                          {d.period}
                        </p>
                        <b>
                          ${d.total.toLocaleString()} total <i>✓</i>
                        </b>
                        <small>{d.fees}</small>
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            {map && (
              <div className="map">
                <div className="road r1" />
                <div className="road r2" />
                <div className="road r3" />
                <span className="m1">Frisco Square</span>
                <span className="m2">Stonebriar</span>
                {results.map((d) => (
                  <button
                    className="marker"
                    key={d.id}
                    style={{ left: `${d.xy[0]}%`, top: `${d.xy[1]}%` }}
                  >
                    {d.total.toLocaleString()}
                  </button>
                ))}
                <button className="area">Search this area</button>
                <div className="zoom">
                  <button>+</button>
                  <button>−</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {compare.length > 0 && (
        <div className="compare">
          <b>{compare.length}</b>
          <span>
            <strong>
              {compare.length} rental{compare.length > 1 ? "s" : ""} selected
            </strong>
            <small>Select up to 3 to compare true costs</small>
          </span>
          <button onClick={() => setCompare([])}>Clear</button>
          <button>Compare now</button>
        </div>
      )}

      {ai && (
        <div className="backdrop" onClick={() => setAi(false)}>
          <section className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="close" onClick={() => setAi(false)}>
              ×
            </button>
            <b className="ai-icon">
              <I n="spark" />
            </b>
            <span className="eyebrow">RentWise copilot</span>
            <h2>What kind of rental do you need?</h2>
            <p>Use natural language. I’ll turn your needs into filters and compare the complete cost.</p>
            <form onSubmit={ask}>
              <textarea
                autoFocus
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Find me a quiet 1-bedroom in Frisco under $1,600, with covered parking and a gym…"
              />
              <div>
                <small>Try: “SUV at DFW for 5 days”</small>
                <button>
                  <I n="spark" /> Find my rental
                </button>
              </div>
            </form>
            <footer>✓ No hidden fees　 ✓ Grounded in listing data　 ✓ You stay in control</footer>
          </section>
        </div>
      )}
    </main>
  );
}
