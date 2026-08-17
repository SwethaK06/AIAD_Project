CREATE TABLE vehicles (
    vehicle_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    fuel_type VARCHAR(30) NOT NULL,
    vehicle_weight_kg DECIMAL(10, 2),
    maximum_load_kg DECIMAL(10, 2),
    status VARCHAR(30) DEFAULT 'Active',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deliveries (
    delivery_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id BIGINT NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    load_weight_kg DECIMAL(10, 2),
    delivery_status VARCHAR(30) DEFAULT 'Pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_delivery_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id)
        ON DELETE CASCADE
);

CREATE TABLE routes (
    route_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    delivery_id BIGINT NOT NULL,
    route_name VARCHAR(100),
    distance_km DECIMAL(10, 2) NOT NULL,
    estimated_duration_minutes DECIMAL(10, 2),
    traffic_level VARCHAR(30),
    road_type VARCHAR(50),
    is_recommended BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_route_delivery
        FOREIGN KEY (delivery_id)
        REFERENCES deliveries(delivery_id)
        ON DELETE CASCADE
);

CREATE TABLE traffic_data (
    traffic_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    route_id BIGINT NOT NULL,
    congestion_level VARCHAR(30),
    average_speed_kmh DECIMAL(8, 2),
    delay_minutes DECIMAL(8, 2),
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_traffic_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id)
        ON DELETE CASCADE
);

CREATE TABLE emission_predictions (
    prediction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    route_id BIGINT NOT NULL,
    predicted_emission_g_km DECIMAL(12, 4) NOT NULL,
    predicted_total_emission_g DECIMAL(12, 4),
    model_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prediction_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id)
        ON DELETE CASCADE
);

CREATE TABLE vehicle_readings (
    reading_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id BIGINT NOT NULL,
    speed_kmh DECIMAL(8, 2),
    fuel_consumption_litres DECIMAL(10, 3),
    actual_emission_g_km DECIMAL(12, 4),
    idling_duration_minutes DECIMAL(10, 2),
    engine_temperature_c DECIMAL(8, 2),
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_reading_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id)
        ON DELETE CASCADE
);

CREATE TABLE maintenance_alerts (
    alert_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id BIGINT NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    alert_description TEXT,
    severity VARCHAR(20),
    alert_status VARCHAR(30) DEFAULT 'Open',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_alert_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id)
        ON DELETE CASCADE
);

CREATE TABLE carbon_savings (
    saving_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    delivery_id BIGINT NOT NULL,
    original_emission_g DECIMAL(12, 4),
    optimised_emission_g DECIMAL(12, 4),
    emission_saved_g DECIMAL(12, 4),
    estimated_cost_saved DECIMAL(12, 2),
    calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_saving_delivery
        FOREIGN KEY (delivery_id)
        REFERENCES deliveries(delivery_id)
        ON DELETE CASCADE
);

-- Stores the route selected by the user from the UI
CREATE TABLE trips (
    trip_id VARCHAR(36) PRIMARY KEY,

    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,

    origin_coords VARCHAR(100) NOT NULL,
    dest_coords VARCHAR(100) NOT NULL,

    vehicle_type VARCHAR(50) NOT NULL,
    cargo_weight_kg DECIMAL(10, 2) NOT NULL,

    chosen_route_id VARCHAR(50) NOT NULL,

    actual_co2_kgco2e DECIMAL(12, 4),
    distance_km DECIMAL(10, 2)
);

INSERT INTO vehicles (
    registration_number,
    vehicle_type,
    fuel_type,
    vehicle_weight_kg,
    maximum_load_kg
)
VALUES (
    'SGB1234A', almost I I thought we'll not go okay on the document UI to the database to do tomorrow we just so much to do man I have been used to dress right now I used to tree credit in tennis anymore are graded on the line I refuse to get low tomorrow next week we had time to do in afternoon the supply chains control Al Singap like ten thirty two before that means you have to be back here like we will come back here at like nine three we'll go over for dinner like seven come back like nine thirty stokicho and do a project right now yeah I have a project bro also send me your location so you can tomorrow what time after fivedoes this text do what I'm free bring you in then my question you say like oh like how long is you gonna be here in Sh where just touch it out to see if they don't ask you should be able to sleep over tomorrow without inverse once more they have tomorrow I see okay the navigation things right yeah santers don't a stock on unlucky cookie actually anywhere we can just get the bike or your dad's calling you don't even like yeah we can just rent a bike it's like everywhere imagine attacking that'd be fine tomorrow I won't be packed combo is that beer no ball that is three times suns were strongly refaited where no where we'll drink at my place in little world drink first then go out yeah we did sea I'll keep your eyes in phro thank you starting in the middle slap zero citrus we'll get citrus on graph confirm to clear the bumps or relax I'm actually ten thousand dollar fine if I like five hundred each that's actually mad the bro open the friends in shapes for the miracle work from but I can't pay seven hundred for months I mean I'm gonna be bored as why does it work from an actual office and every other company wanted like Singaporeans calling after like like four thirty luck if I'm doing extra hours okay okay hello being evaluated unfortunately. xanhal has abandoned me this called i had to deal with him no no he just called i also let it confirm are you okay with next week on day presentation is on afternoon yeah we have to he's only three after like four thirty thought for i kind of only quiring stenders the priority was that priority way if a wan you put in the goal docs new i to mountain engine most priority it's like what the what's the values inside priority rate balance yeah the values risk balance priority is the decision so like let's say you will need to say how how do you want to deliver it the most ego friendly one the fastest one or the most balanced one so priority it's is does this trial he's asking how much it is by the way fifty dollars I haven't I haven't reserved any days later's fully in vish there's one fish that is my close friend's me to make a group chat for the for the priority week is just to drop down for w for just green balance and pastors that's a only these three options something about basic so today I'll be localizing my container first I will work on the project upgrade link it up with tenshall be fine for the medical tire how many types of vehicles are like there processing yes how many vehicle types I feel like it's better to make a drop down for that also marketicks are sixty dollars oh it's a club fifty on Monday sixty that's like already hundred by I'm cooked yeah you said boy you want to give your own seafood boy recipe that was the most reputable but I think there was an offer for another seafood are you sure it's fifty yeah it is not like a you have to order your own things you know you order your own stuff a seafood mag is like six with muscles prawns and taps a dual bag is thirty five so if you share it's like plus yeah smoke salsage sweet pocorn one eighty nine sixty three bungee baked with funds that share lobster mi pok Sri Lanka buns amazing internship is starting yang is okay it's okay you only live once we take the duo bag and then we get something else aside I think we get a dual plus and then other sides we need to reason a spot I have to I think I reserved tomorrow on Monday Monday night instead of spot I mean I'm not talking about the seafood dreil talking about marquee the club's living by next week so I don't really have a better time and I don't have anyone else with me he's only I'm not going with Danish cause I don't even know the guy of God in Smanhore Slap, did you want hear that anyone other than people on this call than the people in this call? Hello Vision sister who are you calling a bitch is probably gonna hit like around there it's fine it's okay it's okay he do what the price is not the why I'm worried about I got money they did not realize I just left the calln's very high and ran away like a lip or the bitch and you were never going to tell you what I tell you a little story but I was I had to find the urge to not the time I was about to walk K my friend told me let's let's perfect kill it's a club name is it you know Marina where is it told me oh it's like the first time the second time I was walking with my I was walking them again walk past alright I'll see you how will you come in come in and let's go in nah and do that man a man of ground just and pray and look at the sky and plus mark is like all the people balances like bounces okay calling me a bouncer big buffer can give me a second to lock something in and okay so my my such a long story she went to the club club holy shit changed changes the person and changes fifty four messages fifty four messages in the instagram VM so like fifty four from what the guy sitting on how do they find her Instagram even though you the corrupt people as I'll never find myself any thought maybe my way literally no and I know he was willing to come to the club that Singapore crowd and Uk crowd are different yeah thanks including myself we need to find someone else need to find those European guys gold clubbing stocks you never been to a club what my ban I'm trying to see my loop rocks like the over stimulating under experience I want to try and a pub actually nice to a story of me no you have not told you a story about me being invited by my secondary school teacher yes you have hi yeah hopefully good for the best for the best actually can write to get dual plus dual bag we can get exactly fifty but no that doesn't take into account the the gst give me like about thirty minutes I will refine my my bah I can send you the I can send I can mostly gith up you put it inside and you try and run the model and make sure that it can go to U inside ya can I connect my thing now my database or do I want to do tomorrow drink class I just need a few minutes a thirty minutes to test okay so later today honestly the core right now is so air generated but I'll I kind of presume that by Saturday or Sunday it's gonna look nice I'm actually gonna like cut your machine is cool and make sure that it works and make sure that the code is integral and each of us will need to do a read me file and ya so I think that that's what we will turn most of tells for me I'm just I just thinking now today you just want to choose the requirements of what you want to see but in the back end we'll we'll do all the documentation nice let me push my stuff first in the morning Friday cause Saturday the DJ mange cause you were going to comment bro this weekend I'm gonna be jump back so can we call Friday morning or Friday yeah Friday Friday afternoon ish twelve cause at the I can help Friday Saturday I'm busy twelve PM Fridays my sticker sticker oh hell no he actually said that no no it's a sticker of an Indian guy Indian child with headphones sticking into his butt and he's listening to it's not funny what he talking about what he talking about many container routes let's see if this holding works means from low normal high second
    'Delivery Van',
    'Diesel',
    1800,
    700
);