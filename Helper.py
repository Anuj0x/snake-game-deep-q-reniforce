import matplotlib.pyplot as plt
try:
    from IPython import display
    IPython_available = True
except ImportError:
    IPython_available = False

plt.ion()

def plot(scores, mean_scores):
    if IPython_available:
        display.clear_output(wait=True)
        display.display(plt.gcf())

    plt.clf()
    plt.title("Training...")
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1,scores[-1],str(scores[-1]))
    plt.text(len(mean_scores)-1,mean_scores[-1],str(mean_scores[-1]))
    plt.draw()
    if IPython_available:
        plt.show(block=False)
    else:
        plt.pause(.1)
