/* ==========================================================================
   Andamana — tour catalogue
   Single source of truth for every grid, the search index and the detail page.
   Prices are in Thai baht, per person, low-season rate.
   ========================================================================== */
window.ANDAMANA_TOURS = [
  {
    slug: "phi-phi-ferry",
    title: "Phi Phi Island ferry ticket",
    lead: "Open return crossing from Rassada Pier",
    img: "assets/img/card-bamboo.svg",
    price: 350,
    duration: "2 hr crossing",
    group: "Scheduled ferry",
    departs: "Phuket",
    tags: ["transfer", "budget"],
    badge: "Transfer",
    summary:
      "The workhorse crossing every island hopper takes at least once. Air-conditioned lower deck, open sun deck upstairs, and a bow that points straight at the karsts for the last thirty minutes.",
    highlights: [
      "Four sailings a day, open return valid for 30 days",
      "Free hotel pickup inside Phuket Town and Patong",
      "Luggage handling at both piers included"
    ],
    itinerary: [
      { t: "08:00", h: "Rassada Pier", c: "Check in at the Andamana desk, collect your boarding band and drop your bags with the porters." },
      { t: "08:30", h: "Cast off", c: "Head south past Koh Racha with coffee from the galley. Sun deck opens once we clear the harbour wall." },
      { t: "10:30", h: "Tonsai Bay", c: "Arrive into Phi Phi Don. Onward long-tails to Long Beach and Laem Tong leave from the same jetty." }
    ],
    includes: ["Return ferry ticket", "Pier transfer in Phuket", "Marine national park insurance", "Luggage porterage"],
    excludes: ["National park entry fee (400 B)", "Meals on board"],
    gallery: ["assets/img/card-bamboo.svg", "assets/img/card-mayabay.svg", "assets/img/banner-story.svg"]
  },
  {
    slug: "pileh-maya-longtail",
    title: "Long-tail to Pileh Lagoon, Maya Bay & Loh Samah",
    lead: "Three hours, private boat, no crowds",
    img: "assets/img/card-pileh.svg",
    price: 1499,
    duration: "3 hr",
    group: "Private, up to 6",
    departs: "Phi Phi Don",
    tags: ["island", "private", "snorkel"],
    badge: "Private",
    summary:
      "Your own long-tail and captain for three hours. We leave before the day-trip fleet arrives, which is the whole trick: Pileh at glass-flat first light, Maya Bay with the sand to yourself, Loh Samah for the drop-off.",
    highlights: [
      "06:30 departure beats every Phuket day boat by two hours",
      "Snorkel gear, dry bag and cold towels on board",
      "Captain who has fished this bay for twenty-two years"
    ],
    itinerary: [
      { t: "06:30", h: "Tonsai jetty", c: "Meet your captain, stow your bag under the bow tarp and slide out of the bay while it is still grey." },
      { t: "07:00", h: "Pileh Lagoon", c: "Enter the lagoon on slack water. Forty minutes of swimming inside a wall of limestone with nothing else afloat." },
      { t: "08:00", h: "Maya Bay", c: "Land on the north beach, walk the boardwalk to the viewpoint, back on the water before the fleet rounds the headland." },
      { t: "09:00", h: "Loh Samah", c: "Snorkel the drop-off — staghorn coral, sergeant majors, and the occasional blacktip reef shark cruising the sand." }
    ],
    includes: ["Private long-tail and captain", "Snorkel mask and fins", "Drinking water and fruit", "Dry bag hire"],
    excludes: ["National park fee (400 B)", "Gratuity for your captain"],
    gallery: ["assets/img/card-pileh.svg", "assets/img/card-mayabay.svg", "assets/img/card-bamboo.svg", "assets/img/banner-journal.svg"]
  },
  {
    slug: "phi-phi-don-loop",
    title: "Long-tail loop around Phi Phi Don",
    lead: "Four hours of bays, viewpoints and shade",
    img: "assets/img/card-mayabay.svg",
    price: 2499,
    duration: "4 hr",
    group: "Private, up to 6",
    departs: "Phi Phi Don",
    tags: ["island", "private", "snorkel"],
    badge: "Highlight",
    summary:
      "A slow circuit of the island most visitors only see from a pier. Monkey Beach, the Nui Bay swim-through, Laem Tong for lunch under the casuarinas, then back along the east coast with the light behind you.",
    highlights: [
      "Six stops, four of them swimmable",
      "Lunch at a Moken village kitchen on Laem Tong",
      "Return along the lee shore — flat water all the way home"
    ],
    itinerary: [
      { t: "09:00", h: "Tonsai", c: "Push off north with the tide, hugging the cliffs past the Viking cave." },
      { t: "09:40", h: "Monkey Beach", c: "Twenty minutes ashore. Keep food in the dry bag — the macaques are professionals." },
      { t: "10:30", h: "Nui Bay", c: "Snorkel the swim-through under the north headland, then coffee on the sand." },
      { t: "12:00", h: "Laem Tong", c: "Grilled snapper, papaya salad and sticky rice at a village kitchen with the boat pulled up outside." },
      { t: "13:00", h: "East coast run", c: "Home the long way past Hin Klang reef with the sun on your back." }
    ],
    includes: ["Private long-tail and captain", "Lunch at Laem Tong", "Snorkel gear", "Water, fruit and ice"],
    excludes: ["National park fee (400 B)", "Alcohol"],
    gallery: ["assets/img/card-mayabay.svg", "assets/img/card-bamboo.svg", "assets/img/card-pileh.svg"]
  },
  {
    slug: "phi-phi-bamboo-6hr",
    title: "Phi Phi Don + Phi Phi Leh + Bamboo Island",
    lead: "The full six-hour highlights run",
    img: "assets/img/card-bamboo.svg",
    price: 2999,
    duration: "6 hr",
    group: "Private, up to 8",
    departs: "Phi Phi Don",
    tags: ["island", "private", "snorkel"],
    badge: "Best seller",
    summary:
      "Everything in one day, sequenced so you are always ahead of the crowd: Leh at dawn, Don for lunch, and Bamboo Island in the afternoon when the light turns the sandbar white and the day boats have gone.",
    highlights: [
      "Three islands, seven stops, one boat all day",
      "Bamboo Island after 15:00 — the bar is empty and the water is glass",
      "Fresh fruit, ice and a proper cool box on board"
    ],
    itinerary: [
      { t: "07:00", h: "Phi Phi Leh", c: "Pileh Lagoon and Maya Bay before the fleet, exactly as on the three-hour trip." },
      { t: "10:00", h: "Monkey Beach", c: "A short stop on the way back up the west coast." },
      { t: "12:00", h: "Lunch ashore", c: "Beach kitchen on Phi Phi Don, feet in the sand, an hour out of the sun." },
      { t: "14:30", h: "Bamboo Island", c: "Cross to the sandbar. Snorkel the north reef, walk the spit, swim until the light goes gold." },
      { t: "17:00", h: "Tonsai", c: "Back into the bay with the karsts turning pink behind you." }
    ],
    includes: ["Private boat and crew for 6 hours", "Lunch and afternoon fruit", "Snorkel gear and dry bags", "Reef-safe sunscreen"],
    excludes: ["National park fees (400 B x2)", "Gratuities"],
    gallery: ["assets/img/card-bamboo.svg", "assets/img/card-mayabay.svg", "assets/img/card-pileh.svg", "assets/img/banner-story.svg"]
  },
  {
    slug: "hong-islands-kayak",
    title: "Hong Islands sea-kayak day",
    lead: "Paddle the hidden lagoons of Krabi",
    img: "assets/img/card-hongisle.svg",
    price: 2200,
    duration: "7 hr",
    group: "Small group, max 10",
    departs: "Krabi",
    tags: ["kayak", "island", "group"],
    badge: "Kayak",
    summary:
      "Two-person sit-on-top kayaks and a guide who reads tide tables for a living. The hongs — collapsed cave rooms open to the sky — are only enterable for about ninety minutes either side of low water, and that is exactly when we go in.",
    highlights: [
      "Two hongs entered at the right state of tide",
      "Mangrove channel paddle with kingfishers and mudskippers",
      "Thai lunch cooked on the support boat"
    ],
    itinerary: [
      { t: "08:00", h: "Ao Nang pickup", c: "Minibus to the pier, safety brief and paddle fitting on the beach." },
      { t: "09:30", h: "Hong Island", c: "Paddle the eastern wall and slip through the entrance tunnel into the first hong." },
      { t: "11:00", h: "Lading Island", c: "Snorkel stop on the sheltered side while the tide turns." },
      { t: "12:30", h: "Lunch afloat", c: "Green curry, rice and pineapple on the support boat, moored in the lee." },
      { t: "14:00", h: "Mangrove channel", c: "A slow paddle through the mangroves before the ride back." }
    ],
    includes: ["Kayak, paddle and buoyancy aid", "English-speaking guide", "Lunch and drinking water", "Hotel transfer in Ao Nang and Krabi Town"],
    excludes: ["National park fee (300 B)", "Wetsuit hire"],
    gallery: ["assets/img/card-hongisle.svg", "assets/img/card-kayak.svg", "assets/img/banner-journal.svg"]
  },
  {
    slug: "phang-nga-james-bond",
    title: "Phang Nga Bay & Koh Tapu by speedboat",
    lead: "Limestone towers, sea caves, stilt village",
    img: "assets/img/card-jamesbond.svg",
    price: 2650,
    duration: "8 hr",
    group: "Small group, max 16",
    departs: "Phang Nga",
    tags: ["island", "group", "culture"],
    badge: "Icon",
    summary:
      "The bay that made Thai limestone famous. Koh Tapu leaning out of the water, the sea caves at Koh Panak, and lunch at Koh Panyee — a Muslim fishing village built entirely on stilts, complete with a floating football pitch.",
    highlights: [
      "Sea-cave canoe through Koh Panak's dark tunnels",
      "Lunch in the stilt village of Koh Panyee",
      "Swim stop at Naka Island on the way home"
    ],
    itinerary: [
      { t: "07:30", h: "Ao Por pier", c: "Board the speedboat, life jackets and a quick brief from the guide." },
      { t: "08:45", h: "Koh Panak", c: "Swap to canoes and paddle into the cave system with head torches." },
      { t: "10:30", h: "Koh Tapu", c: "The famous leaning stack, photographed from the water and the beach behind it." },
      { t: "12:00", h: "Koh Panyee", c: "Walk the boardwalks, eat where the village eats, watch a game on the floating pitch." },
      { t: "14:30", h: "Naka Island", c: "Last swim and snorkel before the run back to Phuket." }
    ],
    includes: ["Speedboat and guide", "Canoe session with paddler", "Lunch at Koh Panyee", "Hotel transfer in Phuket"],
    excludes: ["National park fee (300 B)", "Drinks at lunch"],
    gallery: ["assets/img/card-jamesbond.svg", "assets/img/card-kayak.svg", "assets/img/banner-cta.svg"]
  },
  {
    slug: "similan-liveaboard",
    title: "Similan Islands three-day liveaboard",
    lead: "Nine dives, two nights, open ocean",
    img: "assets/img/card-similan.svg",
    price: 18500,
    duration: "3 days / 2 nights",
    group: "Max 12 divers",
    departs: "Khao Lak",
    tags: ["dive", "liveaboard"],
    badge: "Diving",
    summary:
      "Granite boulders the size of buildings, soft-coral walls, and the best visibility in the Andaman. Nine dives across Richelieu Rock, Koh Bon and the Similan west ridges, with air-conditioned twin cabins and a galley that never stops.",
    highlights: [
      "Nine guided dives including a night dive at Koh Bon",
      "Nitrox available at no extra cost",
      "Twin cabins with private heads and air conditioning"
    ],
    itinerary: [
      { t: "Day 1", h: "Khao Lak to Similan 9", c: "Board at 18:00, sail overnight, check dive at first light on the east ridge." },
      { t: "Day 2", h: "Koh Bon & Koh Tachai", c: "Four dives including the Koh Bon manta ridge, then a night dive off the pinnacle." },
      { t: "Day 3", h: "Richelieu Rock", c: "Two dawn dives on the purple soft-coral horseshoe before the run home." }
    ],
    includes: ["All dives, tanks and weights", "Full board and soft drinks", "Twin cabin", "Marine park fees"],
    excludes: ["Equipment rental (2,500 B for 3 days)", "Certification courses"],
    gallery: ["assets/img/card-similan.svg", "assets/img/card-kohtao.svg", "assets/img/banner-cta.svg"]
  },
  {
    slug: "koh-tao-discover-dive",
    title: "Koh Tao discover scuba day",
    lead: "Two dives, no licence needed",
    img: "assets/img/card-kohtao.svg",
    price: 3400,
    duration: "6 hr",
    group: "Max 2 per instructor",
    departs: "Koh Tao",
    tags: ["dive", "beginner"],
    badge: "Beginner",
    summary:
      "The gentlest introduction to breathing underwater there is. A shallow bay to learn in, then two proper dives at Japanese Gardens and White Rock with an instructor who never leaves your shoulder.",
    highlights: [
      "Two-to-one instructor ratio, always",
      "All equipment and a logged dive to carry forward",
      "Reef briefing you will still remember next year"
    ],
    itinerary: [
      { t: "08:00", h: "Sairee Beach", c: "Theory over coffee, then kit fitting and a skills session in waist-deep water." },
      { t: "10:00", h: "Japanese Gardens", c: "First dive, twelve metres, hard coral and a resident school of batfish." },
      { t: "12:30", h: "White Rock", c: "Second dive after a surface interval and lunch on the boat." }
    ],
    includes: ["All dive equipment", "Two guided dives", "Lunch and water", "Digital dive log"],
    excludes: ["Underwater photos (600 B)", "PADI certification"],
    gallery: ["assets/img/card-kohtao.svg", "assets/img/card-similan.svg", "assets/img/banner-journal.svg"]
  },
  {
    slug: "sunset-catamaran",
    title: "Sunset catamaran with dinner service",
    lead: "Four hours under sail off Chalong",
    img: "assets/img/card-sunsetsail.svg",
    price: 4200,
    duration: "4 hr",
    group: "Max 20",
    departs: "Phuket",
    tags: ["sunset", "sail", "group"],
    badge: "Sunset",
    summary:
      "A 44-foot cruising catamaran, sails up the moment we clear the moorings, and a galley team plating Thai small dishes as the sun drops behind Koh Lon. Swim stop at anchor before the light goes.",
    highlights: [
      "Actual sailing, not a motor boat with a mast",
      "Six-course Thai sharing menu cooked aboard",
      "Netting up front — the best seat on the water"
    ],
    itinerary: [
      { t: "15:30", h: "Chalong Pier", c: "Tender out to the catamaran, welcome drink, and a quick brief from the skipper." },
      { t: "16:15", h: "Under sail", c: "Main and jib up, heading west between Koh Lon and Koh Hae." },
      { t: "17:30", h: "Swim stop", c: "Anchor in a sheltered bay for a swim off the stern ladder." },
      { t: "18:20", h: "Sunset service", c: "Dinner served on deck as the sun goes down behind the islands." }
    ],
    includes: ["Four-hour sail", "Thai sharing dinner", "Open bar (beer, wine, soft drinks)", "Pier transfer"],
    excludes: ["Spirits", "Hotel transfer outside Chalong"],
    gallery: ["assets/img/card-sunsetsail.svg", "assets/img/banner-cta.svg", "assets/img/card-lantasunset.svg"]
  },
  {
    slug: "lanta-sunset-viewpoint",
    title: "Koh Lanta west coast at golden hour",
    lead: "Viewpoints, old town, seafood on stilts",
    img: "assets/img/card-lantasunset.svg",
    price: 1650,
    duration: "5 hr",
    group: "Private, up to 4",
    departs: "Koh Lanta",
    tags: ["sunset", "private", "culture"],
    badge: "Golden hour",
    summary:
      "An afternoon drive down the spine of Lanta Yai with a driver who knows which viewpoints face west. Ends on a stilt terrace in the old town with grilled squid and the sun going into the Andaman.",
    highlights: [
      "Three west-facing viewpoints, timed to the light",
      "Lanta Old Town before the tour buses",
      "Table booked over the water for sunset"
    ],
    itinerary: [
      { t: "14:00", h: "Hotel pickup", c: "Anywhere between Klong Dao and Kantiang Bay." },
      { t: "15:00", h: "Khao Mai Kaew", c: "Short walk to the ridge viewpoint over the whole west coast." },
      { t: "16:30", h: "Lanta Old Town", c: "Wander the boardwalk, stop at the sea-gypsy museum, coffee in a hundred-year-old shophouse." },
      { t: "18:00", h: "Sunset dinner", c: "Grilled squid, whole fish and morning glory on a stilt terrace." }
    ],
    includes: ["Private car and driver", "Coffee stop", "Sunset dinner reservation", "Bottled water"],
    excludes: ["Dinner bill", "Viewpoint entry (50 B)"],
    gallery: ["assets/img/card-lantasunset.svg", "assets/img/banner-cta.svg", "assets/img/card-sunsetsail.svg"]
  },
  {
    slug: "lipe-sandbar-dawn",
    title: "Koh Lipe sandbar at first light",
    lead: "Three islands before breakfast",
    img: "assets/img/card-lipe.svg",
    price: 1250,
    duration: "3 hr",
    group: "Private, up to 5",
    departs: "Koh Lipe",
    tags: ["island", "private", "sunset"],
    badge: "Sunrise",
    summary:
      "Out at 05:45 in a long-tail to the sandbar that appears between Lipe and Koh Kra at low water. Coffee in a thermos, the whole Tarutao chain turning pink, and back on Pattaya Beach before the first shop opens.",
    highlights: [
      "The sandbar only exists at low tide — we time it exactly",
      "Snorkel the Koh Kra wall in flat morning water",
      "Thermos coffee and Thai custard buns aboard"
    ],
    itinerary: [
      { t: "05:45", h: "Sunrise Beach", c: "Wade out to the long-tail in the dark and slip out to the east." },
      { t: "06:15", h: "The sandbar", c: "Land on a strip of sand with water on both sides as the sun comes up over Tarutao." },
      { t: "07:15", h: "Koh Kra", c: "Snorkel the wall — parrotfish, giant clams and very little current at this hour." },
      { t: "08:30", h: "Pattaya Beach", c: "Back ashore for breakfast in the village." }
    ],
    includes: ["Private long-tail", "Snorkel gear", "Coffee and pastries", "Beach towel"],
    excludes: ["Tarutao park fee (200 B)", "Breakfast ashore"],
    gallery: ["assets/img/card-lipe.svg", "assets/img/card-hongisle.svg", "assets/img/banner-journal.svg"]
  },
  {
    slug: "mangrove-kayak-half-day",
    title: "Mangrove channels half-day paddle",
    lead: "Quiet water, kingfishers, no engines",
    img: "assets/img/card-kayak.svg",
    price: 980,
    duration: "3.5 hr",
    group: "Small group, max 8",
    departs: "Krabi",
    tags: ["kayak", "group", "wildlife"],
    badge: "Wildlife",
    summary:
      "The antidote to speedboat days. A guided paddle up the Ao Thalane channels at high water, drifting under the root canopy while long-tailed macaques work the banks and collared kingfishers cut across the water ahead of you.",
    highlights: [
      "No engines from the moment you launch",
      "Macaques, kingfishers, monitor lizards and mudskippers",
      "Ideal for first-time paddlers and families"
    ],
    itinerary: [
      { t: "08:30", h: "Ao Thalane", c: "Paddle brief on the ramp, then straight into the main channel on the flood tide." },
      { t: "09:30", h: "The narrows", c: "Duck under the mangrove canopy where the channel closes to two metres wide." },
      { t: "11:00", h: "Karst basin", c: "Open water between two limestone walls — the turnaround point, and the quietest place in Krabi." }
    ],
    includes: ["Kayak and buoyancy aid", "Guide", "Water and seasonal fruit", "Dry bag"],
    excludes: ["Hotel transfer (200 B per person)", "Lunch"],
    gallery: ["assets/img/card-kayak.svg", "assets/img/card-hongisle.svg", "assets/img/banner-journal.svg"]
  }
];

/* departure points used by the mega menu and the tours page */
window.ANDAMANA_DEPARTURES = [
  { name: "Koh Chang", count: 6 },
  { name: "Chumphon Sea", count: 4 },
  { name: "Koh Tao", count: 9 },
  { name: "Koh Samui", count: 11 },
  { name: "Ranong", count: 3 },
  { name: "Phang Nga", count: 8 },
  { name: "Phuket", count: 24 },
  { name: "Krabi", count: 19 },
  { name: "Koh Lanta", count: 7 },
  { name: "Trang Islands", count: 5 },
  { name: "Koh Lipe", count: 6 },
  { name: "Koh Adang", count: 2 }
];
