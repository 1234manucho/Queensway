"""Editable school copy and the six school photographs supplied by Queensway."""
# Existing article image keys stay stable so saved posts need no database migration.
PHOTOS = {
    'classroom': {'file': 'learning-through-play.jpg', 'label': 'Learning through play',
                  'alt': 'Two Queensway pupils exploring and balancing outdoors in yellow and green uniforms',
                  'width': 1599, 'height': 1066, 'position': '50% 50%'},
    'discover': {'file': 'queensway-learner.jpg', 'label': 'Queensway learner',
                 'alt': 'A smiling Queensway learner wearing the green and mustard yellow school uniform',
                 'width': 1066, 'height': 1600, 'position': '50% 22%'},
    'create': {'file': 'playground-friends.jpg', 'label': 'Playground friends',
               'alt': 'Queensway pupils standing together in front of colourful playground equipment',
               'width': 1600, 'height': 1066, 'position': '50% 50%'},
    'together': {'file': 'outdoor-discovery.jpg', 'label': 'Outdoor discovery',
                 'alt': 'Queensway children and adults enjoying an outdoor activity among trees',
                 'width': 1280, 'height': 853, 'position': '50% 50%'},
    'class-group': {'file': 'our-school-community.jpg', 'label': 'Our school community',
                    'alt': 'Queensway pupils in mustard yellow uniforms gathered for a class photograph outside school',
                    'width': 1600, 'height': 1066, 'position': '50% 50%'},
    'campus': {'file': 'queensway-campus.jpg', 'label': 'Queensway campus',
               'alt': 'The Queensway Early Years school exterior with green signs and a colourful boundary wall',
               'width': 1280, 'height': 853, 'position': '50% 50%'},
}
VISION = 'To inspire a thirst of learning within a challenging yet inclusive environment.'
MISSION = ('To provide a safe, appropriate, nurturing environment which stimulates early learning, '
           'promotes each child’s social/emotional, cognitive and physical growth as well as a '
           'positive self-image and a love for learning.')
VALUES = [
    ('Character building', 'Growing into thoughtful, confident little people.', 'spark'),
    ('Integrity', 'Learning to be honest, fair and true to ourselves.', 'scale'),
    ('Respect', 'Making room for every voice, idea and individual.', 'hand'),
    ('Kindness', 'Finding little ways to care for one another, every day.', 'heart'),
    ('Team work', 'Discovering how much more we can do together.', 'people'),
]
PROGRAMMES = [
    {'slug': 'early-learners', 'name': 'Early learners', 'eyebrow': 'A happy beginning', 'number': '01',
     'description': 'A gentle introduction to new friendships, new routines and a world of sensory discovery.',
     'image': 'discover', 'focus': ['Settling in and feeling secure', 'Sensory exploration', 'Listening and early language', 'Learning alongside others']},
    {'slug': 'growing-explorers', 'name': 'Growing explorers', 'eyebrow': 'Room to wonder', 'number': '02',
     'description': 'Stories, building, art and imaginative play turn everyday questions into joyful discoveries.',
     'image': 'classroom', 'focus': ['Creative and imaginative play', 'Stories, sounds and conversation', 'Early number and patterns', 'Curiosity about our world']},
    {'slug': 'ready-for-school', 'name': 'Ready for school', 'eyebrow': 'Confidence for what’s next', 'number': '03',
     'description': 'Building independence, connection and a love of learning for the exciting steps ahead.',
     'image': 'create', 'focus': ['Independence and self-expression', 'Early literacy and numeracy', 'Problem-solving together', 'Confidence with new routines']},
]
GALLERY = [
    {'image': 'class-group', 'category': 'School life', 'title': 'Our Queensway community', 'caption': 'Shared beginnings, growing friendships and a place to belong.'},
    {'image': 'classroom', 'category': 'Outdoors', 'title': 'Little steps. Big discoveries.', 'caption': 'Exploring, balancing and discovering through outdoor play.'},
    {'image': 'discover', 'category': 'School life', 'title': 'Proud to be Queensway', 'caption': 'A bright smile in our school’s green and mustard yellow.'},
    {'image': 'create', 'category': 'School life', 'title': 'Friends in the playground', 'caption': 'Together in a colourful space made for play and discovery.'},
    {'image': 'together', 'category': 'Outdoors', 'title': 'Room to run. Freedom to wonder.', 'caption': 'Fresh air, movement and shared adventures among the trees.'},
    {'image': 'campus', 'category': 'Our campus', 'title': 'Welcome to our school', 'caption': 'A little look at the place where our learning journey begins.'},
]
ARTICLES = [
    {'slug': 'little-questions-big-discoveries', 'title': 'Little questions, big discoveries', 'category': 'Learning at home',
     'excerpt': 'Every “why?” is the beginning of something wonderful. Make space for curiosity in everyday moments.',
     'image_key': 'discover', 'body': 'A child’s questions open the door to conversation. Pause, listen, and explore an idea together instead of rushing to find the perfect answer.\n\nTry a small discovery walk. Look for different leaf shapes, listen for sounds, or notice how shadows move. Invite your child to describe what they see.\n\nAt home, everyday objects can become a collection to sort, count and compare. Ask open questions such as “What do you notice?” and “What else could we try?”\n\nKeep the experience relaxed and child-led. The pleasure of exploring together matters more than getting an answer right.'},
    {'slug': 'the-magic-of-a-shared-story', 'title': 'The magic of a shared story', 'category': 'Family moments',
     'excerpt': 'A favourite book, a cosy corner and a little time together. Simple ways to bring stories to life.',
     'image_key': 'classroom', 'body': 'Choose a book together and let your child turn the pages. There is no need to hurry through every word. Pictures, expressions and pauses are part of the story too.\n\nInvite your child to guess what happens next, find something in the picture, or give a character a funny voice. Repeating favourite stories can be just as enjoyable as discovering new ones.\n\nWhen the book closes, the story can continue. Make a drawing, retell a favourite moment, or invent a different ending together.'},
    {'slug': 'kindness-in-the-little-things', 'title': 'Kindness in the little things', 'category': 'Growing together',
     'excerpt': 'Sharing a toy, offering a hand, listening to a friend. The everyday moments that help us grow.',
     'image_key': 'together', 'body': 'Kindness often begins in small, ordinary moments. Invite your child to help with a simple task, make a card, or think about how someone else might feel.\n\nNotice a kind action and describe it clearly: “You made space for your friend to sit beside you.” This helps children connect their choices with the people around them.\n\nWhen things feel difficult, make room for feelings. Listening, naming emotions and trying again together are all part of learning to care.'},
]
