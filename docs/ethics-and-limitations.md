# Ethics and limitations

MindScope is a non-diagnostic research prototype. It makes no medical-device
claim, and no output from the public demo should be used for clinical,
screening, treatment, or other healthcare decisions.

Any real deployment would require informed consent and special handling for
biometric and health data. It would need documented retention limits, role-based
access control, encryption in transit with TLS and at rest, authentication,
audit logging, and data minimization. These controls are requirements, not
features delivered by this public portfolio.

Model development also has substantial scientific limitations. Training data
may encode demographic or acquisition bias, class imbalance can distort
performance, and calibration may be inadequate for a new setting. Development
leakage and choosing a model against the test set can make results look stronger
than they are. Video results are additionally constrained by uncertainty about
the feature contract of extracted OpenFace data. Independent external
validation and prospective clinical validation are required before any
clinical-facing interpretation could be considered.

The author served as ML/AI Integration Lead. Product planning and physical
design/3D printing were handled by teammates.
