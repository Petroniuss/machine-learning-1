using Random, Distributions, LinearAlgebra, Statistics, Plots
gr()

"""
    TODO add a legend to each plot!
"""

struct Measurement <: Number
    val::Float64
    err::Float64

    Measurement(values) = begin
        mn = mean(values)
        st = std(values, mean=mn)
        
        return new(mn, st)
    end
end

value(m::Measurement) = m.val

uncertainty(m::Measurement) = m.err

function sampleHypercube(pointsNo, dimensionsNo)
    unifrom = Uniform(-1, 1)
    points  = rand(unifrom, (pointsNo, dimensionsNo))

    return points
end


"""
## Exercise 1
"""
function plotPointsDistribution(dimensions, pointsNo, retry = 10) 
    function groupPointsWithinHypercube(points)
        pointsNo = size(points)[1]

        inner = [ points[i, :] for i=1:pointsNo if norm(points[i, :]) <= 1.0 ]
        outer = [ points[i, :] for i=1:pointsNo if norm(points[i, :]) >  1.0 ]

        return reduce(hcat, inner)', reduce(hcat, outer)'
    end

    function measureDistribution(dimensionsNo)
        points = sampleHypercube(pointsNo, dimensionsNo)
        inner, outer = groupPointsWithinHypercube(points)

        return [size(inner)[1] size(outer)[1]]
    end 

    function measure(dimensionsNo)
        trials = [ measureDistribution(dimensionsNo) for i=1:retry ]
        trials = reduce(vcat, trials)'

        inner = trials[1, :]
        outer = trials[2, :]

        return [ Measurement(inner) Measurement(outer) ]
    end

    measurements = [ measure(dimensionsNo) for dimensionsNo = dimensions ]
    ys = reduce(vcat, measurements)

    plot(scatter(dimensions, ys))
end

"""
## Exercise 2
"""
function plotMeanDistancesBetweenTwoPoints(dimensions, pointsNo, retry = 10)
    function dist(p1, p2)
        return norm(p2 - p1)
    end

    function measureSingle(dimensionsNo)
        points = sampleHypercube(pointsNo, dimensionsNo)
        distances = [ dist(p1, p2) for p1 = points for p2 = points if p1 != p2 ]

        mn = mean(distances)
        sd = std(distances, mean=mn)

        return [mn sd]
    end 

    function measureAverage(dimensionsNo)
        trials = [ measureSingle(dimensionsNo) for i=1:retry ]
        trials = reduce(vcat, trials)'

        mns = trials[1, :]
        sds = trials[2, :]

        return [ Measurement(mns) Measurement(sds) ]
    end

    measurements = [ measureAverage(dimensionsNo) for dimensionsNo = dimensions ]
    ys = reduce(vcat, measurements)

    plot(scatter(dimensions, ys))
end

"""
## Exercise 3
"""
function plotAngleDistributions(pointsNo, dimensionsNo, drawsNo)
    points = sampleHypercube(pointsNo, dimensionsNo)

    function angle(v1, v2)
        return acos(dot(v1, v2) / (norm(v1) * norm(v2)))
    end

    function drawPoints()
        one = rand(1:pointsNo)
        other = rand(1:pointsNo)
        while one == other
            other = rand(1:pointsNo)
        end
        
        return points[one, :], points[other, :]
    end

    function drawVector()
        p1, p2 = drawPoints()
        return p2 - p1
    end

    function draw()
        v1 = drawVector()
        v2 = drawVector()

        return angle(v1, v2)
    end

    angles = [ draw() for i = 1:drawsNo ]
    histogram(angles, bins = :sturges)
end


begin
    plotPointsDistribution(2:10, 1000)
    plotMeanDistancesBetweenTwoPoints(2:50, 100)
    plotAngleDistributions(1000, 8, 1000)
end
