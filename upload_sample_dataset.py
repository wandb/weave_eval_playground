import weave

# Create a challenging evaluation dataset with tricky examples
eval_examples = [
    # Challenging examples - names buried in complex contexts
    {
        "email": "FWD: Issue Report\n\nOriginal sender: tech@company.com\nSubject: Critical Bug\n\nHi team, forwarding this from our client. The customer (Sarah Mitchell) reported that DataProcessor-Pro v2.5 crashes during export. Please investigate ASAP.\n\n—Forwarded by Alex Thompson, Support Lead",
        "expected_name": "Alex Thompson",  # The forwarder, NOT Sarah Mitchell
        "expected_product": "DataProcessor-Pro v2.5",
        "expected_sentiment": "negative",  # Urgent/critical issue
    },
    {
        "email": "RE: Meeting with Dr. Chen\n\nJust to clarify what Alice mentioned in our call - the AI-Assistant tool works great for basic tasks but struggles with complex queries. Overall satisfied though.\n\nBest,\nMichael Rodriguez\nProduct Manager",
        "expected_name": "Michael Rodriguez",  # NOT Dr. Chen or Alice
        "expected_product": "AI-Assistant",
        "expected_sentiment": "positive",  # Overall satisfied despite limitations
    },
    # Extremely challenging - multiple people, products, and misdirection
    {
        "email": "Update from Jane in accounting: CloudSync Plus deployment went smoothly. However, I'm personally experiencing severe delays with the Enterprise Sync Module during peak hours. This is becoming a bottleneck for our quarterly reports.\n\nUrgent attention needed.\n\nRegards,\nDr. Patricia Williams\nCFO",
        "expected_name": "Dr. Patricia Williams",  # NOT Jane
        "expected_product": "Enterprise Sync Module",  # NOT CloudSync Plus
        "expected_sentiment": "negative",  # Urgent attention needed, bottleneck
    },
    {
        "email": "CC: Bob Wilson, Sarah Chen\n\nTeam update: Wilson mentioned SmartHub connectivity issues last week. However, my main concern is with the NetworkBridge Pro v4.2 - it's completely unreliable during video conferences. This is embarrassing in client meetings.\n\nPlease escalate immediately.\n\nDr. Amanda Foster\nSenior Manager, Tech Solutions Inc",
        "expected_name": "Dr. Amanda Foster",  # NOT Bob Wilson or Sarah Chen
        "expected_product": "NetworkBridge Pro v4.2",  # NOT SmartHub
        "expected_sentiment": "negative",  # Embarrassing, unreliable, escalate
    },
    {
        "email": "Following up on Sarah's ticket #4567. She mentioned WorkflowMax stability issues, but that's resolved now. My current problem is with DataSync Enterprise - it's corrupting files during overnight backups. This is a disaster for our compliance audits.\n\nMike O'Brien\nCEO, DataCorp",
        "expected_name": "Mike O'Brien",  # NOT Sarah
        "expected_product": "DataSync Enterprise",  # NOT WorkflowMax
        "expected_sentiment": "negative",  # Disaster, corrupting files
    },
    # Extremely hard - sarcasm and hidden sentiment
    {
        "email": "Wow, the ProSuite 3000 update is just *fantastic*! 🙄 Now nothing works and I've lost 3 hours of work. Really appreciate the 'improved stability' you promised.\n\nThanks for nothing,\nZhang Wei\nFrustrated Developer",
        "expected_name": "Zhang Wei",
        "expected_product": "ProSuite 3000",
        "expected_sentiment": "negative",  # Heavy sarcasm = very negative
    },
    {
        "email": "CONFIDENTIAL - Internal Use Only\n\nRE: Ticket #1234 - CloudVault Investigation\n\nPer our conversation, María García from Legal called to discuss the data breach. While she's satisfied with our response, I'm deeply concerned about CloudVault's encryption protocols. This could expose us to regulatory violations.\n\nRequesting immediate security audit.\n\nConfidentially yours,\nDr. Rebecca Martinez\nChief Security Officer",
        "expected_name": "Dr. Rebecca Martinez",  # NOT María García
        "expected_product": "CloudVault",
        "expected_sentiment": "negative",  # Deeply concerned, regulatory violations
    },
    {
        "email": "Jennifer from IT will handle the technical details, but I need to address the elephant in the room. DataMiner Pro's new 'AI-powered insights' feature is producing completely nonsensical results. Our quarterly projections are now worthless.\n\nThis is unacceptable.\n\n—Dr. Rajesh Patel\nHead of Analytics",
        "expected_name": "Dr. Rajesh Patel",  # NOT Jennifer
        "expected_product": "DataMiner Pro",
        "expected_sentiment": "negative",  # Unacceptable, worthless results
    },
    # Extremely challenging - multiple layers of misdirection
    {
        "email": "Johnson's team loves your software. Smith specifically mentioned how CloudSync transformed their workflow. However, I must report that our implementation of QuantumDB has been an absolute catastrophe. Three weeks of downtime and counting.\n\nDemanding immediate executive intervention.\n\nJames Brown\nCTO, Enterprise Solutions",
        "expected_name": "James Brown",  # NOT Johnson or Smith
        "expected_product": "QuantumDB",  # NOT CloudSync (which others love)
        "expected_sentiment": "negative",  # Absolute catastrophe, demanding intervention
    },
    {
        "email": "Stockholm office feedback: Anna's team reports InvoiceGen crashes frequently during month-end processing. While they've found workarounds, I'm concerned about the reliability for our IPO audit requirements. This could jeopardize our public offering timeline.\n\nEscalating to board level.\n\nLars Eriksson\nCFO, Nordic Enterprises",
        "expected_name": "Lars Eriksson",  # NOT Anna
        "expected_product": "InvoiceGen",
        "expected_sentiment": "negative",  # Jeopardize IPO, board escalation
    },
    # Deceptive context and buried information
    {
        "email": "Thompson's case update attached. Regarding Lee's WorkStation Pro error 0x80004005 - previous tech support was inadequate. However, my real issue is with the CloudRenderer Enterprise license server. It's rejecting valid certificates and blocking our entire 3D animation pipeline.\n\nProduction has been halted for 48 hours.\n\nEmergency response required.\n\nDavid Kim\nVP of Production",
        "expected_name": "David Kim",  # NOT Thompson or Lee
        "expected_product": "CloudRenderer Enterprise",  # NOT WorkStation Pro
        "expected_sentiment": "negative",  # Production halted, emergency
    },
    {
        "email": "Emma from support was incredibly helpful during our integration call. She walked us through the ReportBuilder setup perfectly. Unfortunately, I must escalate a critical performance issue - our quarterly board reports are timing out after 6+ hours. This is completely unacceptable for executive presentations.\n\nImmediate optimization required.\n\nSamantha Park\nCTO, DataFlow Corp",
        "expected_name": "Samantha Park",  # NOT Emma
        "expected_product": "ReportBuilder",
        "expected_sentiment": "negative",  # Critical issue, unacceptable, immediate action needed
    },
    {
        "email": "URGENT: Customer escalation\n\nPierre-Alexandre Dubois called regarding API-Gateway documentation gaps. While he praised the core functionality, I'm writing to report a showstopper bug: the authentication module is leaking memory and crashing our production servers every 4-6 hours.\n\nThis is a P0 incident affecting 50,000+ users.\n\nTechnical Lead: Maria Santos\nIncident Commander",
        "expected_name": "Maria Santos",  # NOT Pierre-Alexandre Dubois
        "expected_product": "API-Gateway",
        "expected_sentiment": "negative",  # Showstopper bug, P0 incident, affecting users
    },
    {
        "email": "Your tech support team's response time is absolutely abysmal - 72 hours for a P1 ticket! However, I must acknowledge that ProductX's core functionality exceeds expectations. But this support experience has damaged our relationship irreparably.\n\nConsidering contract termination.\n\nFrancis O'Sullivan\nDirector of IT Operations",
        "expected_name": "Francis O'Sullivan",
        "expected_product": "ProductX",
        "expected_sentiment": "negative",  # Abysmal support, damaged relationship, considering termination
    },
    # Products with human names - extremely tricky
    {
        "email": "Maxwell's performance has degraded significantly since the last update. Li Chen from our QA team mentioned similar issues, but I'm the one filing this complaint. The software crashes every 30 minutes during peak usage.\n\nThis is affecting our entire customer service operation.\n\nDr. Jennifer Walsh\nOperations Director",
        "expected_name": "Dr. Jennifer Walsh",  # NOT Li Chen
        "expected_product": "Maxwell",  # Maxwell is the product, not a person
        "expected_sentiment": "negative",  # Degraded performance, crashes, affecting operations
    },
    {
        "email": "Gordon from procurement asked me to follow up on the Morgan Analytics Suite deployment. While the initial setup went smoothly, I'm experiencing severe data corruption issues during large dataset processing. Our financial models are now unreliable.\n\nThis threatens our audit compliance.\n\nYuki Tanaka\nSenior Data Analyst",
        "expected_name": "Yuki Tanaka",  # NOT Gordon
        "expected_product": "Morgan Analytics Suite",
        "expected_sentiment": "negative",  # Severe corruption, unreliable, threatens compliance
    },
    # Extreme sarcasm and subtle negativity
    {
        "email": "DataFlow Pro delivers exactly the 'enterprise-grade reliability' your marketing promised. 🙄 Another classic example of your company's commitment to quality. Three system crashes this morning alone.\n\nTruly impressive consistency.\n\nJoão Silva\nProduct Manager, TechFlow Solutions",
        "expected_name": "João Silva",
        "expected_product": "DataFlow Pro",
        "expected_sentiment": "negative",  # Heavy sarcasm throughout, system crashes
    },
    {
        "email": "Kim mentioned ChromaEdit in our team meeting. Honestly, I couldn't care less about photo editing tools right now. My priority is the VideoProcessor Enterprise license that's blocking our entire creative pipeline. Deadlines are approaching fast.\n\nNeed resolution ASAP.\n\nAlex Thompson\nCreative Director",
        "expected_name": "Alex Thompson",  # NOT Kim
        "expected_product": "VideoProcessor Enterprise",  # NOT ChromaEdit
        "expected_sentiment": "negative",  # Blocking pipeline, deadlines, need ASAP resolution
    },
    # Complex product migration scenarios
    {
        "email": "Our TaskMaster to ProjectPro migration was supposed to improve efficiency. Instead, ProjectPro's gantt chart module is corrupting our project timelines. Anne-Marie from the PMO flagged this, but I'm the one dealing with angry stakeholders.\n\nThis is a complete disaster.\n\nRobert Chen\nVP of Engineering",
        "expected_name": "Robert Chen",  # NOT Anne-Marie Rousseau
        "expected_product": "ProjectPro",  # The problematic one
        "expected_sentiment": "negative",  # Complete disaster, angry stakeholders
    },
    {
        "email": "Muhammad's team loves VideoEdit and PhotoEdit for basic tasks. However, I need to escalate a critical issue with AudioEdit Pro - it's introducing artifacts in our podcast production. Our sponsors are threatening to pull contracts due to audio quality issues.\n\nThis is jeopardizing our revenue stream.\n\nSarah Williams\nPodcast Production Manager",
        "expected_name": "Sarah Williams",  # NOT Muhammad
        "expected_product": "AudioEdit Pro",  # The problematic one
        "expected_sentiment": "negative",  # Critical issue, sponsors threatening, jeopardizing revenue
    },
    # Extremely challenging - informal language with serious issues
    {
        "email": "Dmitri from DevOps mentioned SystemMonitor issues last week. Whatever, that's old news. My current nightmare is CloudWatch Enterprise - it's missing 40% of our server alerts. We've had two undetected outages this month.\n\nThis is a security and compliance disaster.\n\nTechnical Director: Alexandra Petrov\nxXx_CloudMaster_xXx",
        "expected_name": "Alexandra Petrov",  # NOT Dmitri, real name in signature
        "expected_product": "CloudWatch Enterprise",  # NOT SystemMonitor
        "expected_sentiment": "negative",  # Nightmare, missing alerts, disaster
    },
    {
        "email": "¡Hola! Carlos Méndez from Finance mentioned FinanceTracker pricing concerns. However, I'm writing about a catastrophic bug in our CryptoTrader Pro implementation. It's executing trades without authorization, resulting in $50K+ losses.\n\nLegal action is being considered.\n\nGracias por su atención urgente,\nDr. Isabella Rodriguez\nChief Financial Officer",
        "expected_name": "Dr. Isabella Rodriguez",  # NOT Carlos Méndez
        "expected_product": "CryptoTrader Pro",  # NOT FinanceTracker
        "expected_sentiment": "negative",  # Catastrophic bug, $50K losses, legal action
    },
    {
        "email": "Re: Jackson's Scheduler App complaint\n\nWhile Jackson's team finds the basic scheduling adequate, I must report a critical flaw in TaskFlow Enterprise. The automated workflow engine is creating infinite loops, consuming 100% CPU and crashing our production servers.\n\nImmediate hotfix required.\n\nPriya Sharma\nHead of IT Infrastructure",
        "expected_name": "Priya Sharma",  # NOT Jackson
        "expected_product": "TaskFlow Enterprise",  # NOT Scheduler App
        "expected_sentiment": "negative",  # Critical flaw, crashing servers, immediate hotfix needed
    },
    {
        "email": "Following up on Jennifer Chen's CloudBackup Pro ticket. While her backup issues are resolved, I'm escalating a more serious problem with DataVault Enterprise. The encryption keys are being corrupted during automated rotations, making 30% of our backups unrecoverable.\n\nThis violates our disaster recovery SLA.\n\nDavid Kim\nIT Operations Manager",
        "expected_name": "David Kim",  # NOT Jennifer Chen
        "expected_product": "DataVault Enterprise",  # NOT CloudBackup Pro
        "expected_sentiment": "negative",  # Serious problem, unrecoverable backups, SLA violation
    },
    {
        "email": "Singh from warehouse called about InventoryMaster earlier. That's handled. My crisis is with SupplyChain Pro - it's double-ordering everything! We now have $2M in excess inventory and our cash flow is destroyed.\n\n😡😡😡 EMERGENCY BOARD MEETING CALLED 😭😭😭\n\nCFO: Patricia Williams\n//SupplyChainNightmare",
        "expected_name": "Patricia Williams",  # NOT Singh
        "expected_product": "SupplyChain Pro",  # NOT InventoryMaster
        "expected_sentiment": "negative",  # Crisis, $2M excess, cash flow destroyed, emergency meeting
    },
]

if __name__ == "__main__":
    weave.init(project_name="evaluation-playground")
    dataset = weave.Dataset(name="email-eval-dataset", rows=eval_examples) # type: ignore
    weave.publish(dataset)
